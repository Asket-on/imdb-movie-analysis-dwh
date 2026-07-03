with raw_crew as (
    select * from {{ source('raw_imdb', 'title_crew') }}
),

cleaned as (
    select
        tconst as movie_id,
        directors as directors_string,
        writers as writers_string,
        case 
            when directors is not null and directors != '' then string_to_array(directors, ',')
            else null
        end as directors_array,
        case 
            when writers is not null and writers != '' then string_to_array(writers, ',')
            else null
        end as writers_array
    from raw_crew
    where tconst is not null
)

select * from cleaned
