with raw_titles as (
    select * from {{ source('raw_imdb', 'title_basics') }}
),

cleaned as (
    select
        tconst as movie_id,
        "titleType" as title_type,
        "primaryTitle" as primary_title,
        "originalTitle" as original_title,
        case when "isAdult" = '1' then true else false end as is_adult,
        case 
            when "startYear" ~ '^[0-9]+$' then "startYear"::integer 
            else null 
        end as release_year,
        case 
            when "endYear" ~ '^[0-9]+$' then "endYear"::integer 
            else null 
        end as end_year,
        case 
            when "runtimeMinutes" ~ '^[0-9]+$' then "runtimeMinutes"::integer 
            else null 
        end as runtime_minutes,
        genres as genres_string,
        case 
            when genres is not null and genres != '' then string_to_array(genres, ',')
            else null
        end as genres_array
    from raw_titles
    where tconst is not null
)

select * from cleaned
