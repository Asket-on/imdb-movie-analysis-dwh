with movies as (
    select * from {{ ref('int_movies_with_ratings') }}
    where directors_string is not null
),

unrolled as (
    select
        movie_id,
        primary_title,
        release_year,
        trim(director_id) as director_id,
        average_rating,
        num_votes
    from movies,
    lateral unnest(string_to_array(directors_string, ',')) as director_id
)

select
    director_id,
    count(distinct movie_id) as total_directed_movies,
    round(avg(average_rating), 2) as avg_rating,
    sum(num_votes) as total_career_votes,
    count(case when average_rating >= 7.5 then 1 end) as hit_movies_count,
    round((count(case when average_rating >= 7.5 then 1 end)::numeric / nullif(count(movie_id), 0)::numeric) * 100, 1) as hit_ratio_percent,
    min(release_year) as career_start_year,
    max(release_year) as career_end_year
from unrolled
where director_id != '' and director_id != '\N'
group by 1
having count(distinct movie_id) >= 1
order by total_career_votes desc
