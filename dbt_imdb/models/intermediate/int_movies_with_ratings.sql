with titles as (
    select * from {{ ref('stg_imdb__titles') }}
),

ratings as (
    select * from {{ ref('stg_imdb__ratings') }}
),

crew as (
    select * from {{ ref('stg_imdb__crew') }}
),

joined as (
    select
        titles.movie_id,
        titles.title_type,
        titles.primary_title,
        titles.original_title,
        titles.is_adult,
        titles.release_year,
        titles.end_year,
        titles.runtime_minutes,
        titles.genres_string,
        titles.genres_array,
        ratings.average_rating,
        ratings.num_votes,
        crew.directors_string,
        crew.writers_string,
        crew.directors_array,
        crew.writers_array
    from titles
    inner join ratings on titles.movie_id = ratings.movie_id
    left join crew on titles.movie_id = crew.movie_id
    where titles.title_type in ('movie', 'tvSeries', 'documentary')
      and ratings.num_votes >= 100
)

select * from joined
