with movies as (
    select * from {{ ref('int_movies_with_ratings') }}
    where genres_string is not null
),

unrolled as (
    select
        movie_id,
        release_year,
        (release_year / 10) * 10 as decade,
        trim(genre) as genre,
        average_rating,
        num_votes,
        runtime_minutes
    from movies,
    lateral unnest(string_to_array(genres_string, ',')) as genre
)

select
    genre,
    decade,
    count(distinct movie_id) as total_movies,
    round(avg(average_rating), 2) as avg_rating,
    round(sum(average_rating * num_votes) / nullif(sum(num_votes), 0), 2) as weighted_avg_rating,
    sum(num_votes) as total_votes,
    round(avg(runtime_minutes), 1) as avg_runtime_minutes
from unrolled
where genre != '' and decade is not null
group by 1, 2
order by decade desc, total_votes desc
