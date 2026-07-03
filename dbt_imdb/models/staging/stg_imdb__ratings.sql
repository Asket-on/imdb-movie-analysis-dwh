with raw_ratings as (
    select * from {{ source('raw_imdb', 'title_ratings') }}
),

cleaned as (
    select
        tconst as movie_id,
        "averageRating"::numeric(3, 1) as average_rating,
        "numVotes"::integer as num_votes
    from raw_ratings
    where tconst is not null
      and "averageRating" is not null
      and "numVotes" is not null
)

select * from cleaned
