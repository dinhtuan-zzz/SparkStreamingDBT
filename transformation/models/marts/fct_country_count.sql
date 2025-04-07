with staging as (
    select * from {{ ref('stg_raw') }}
)

select
    address.country, count(*) as count_by_country
    from staging
    group by address.country
