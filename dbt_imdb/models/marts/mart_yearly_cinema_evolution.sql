with movies as (
    select * from {{ ref('int_movies_with_ratings') }}
    where release_year is not null
)

select
    release_year,
    title_type,
    count(*) as total_releases,
    round(avg(average_rating), 2) as avg_rating,
    round(sum(average_rating * num_votes) / nullif(sum(num_votes), 0), 2) as weighted_avg_rating,
    sum(num_votes) as total_votes,
    round(avg(runtime_minutes), 1) as avg_runtime_minutes
from movies
group by 1, 2
order by release_year desc, total_releases desc
