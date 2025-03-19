{{
    config(
	materialized = "table",
	tags=["staging"]
    )
}}

with raw_data as (
    select *
    from {{source('raw_data', 'daily')}}
)

select * from raw_data
