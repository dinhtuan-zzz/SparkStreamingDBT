{{
    config(
	materialized = "table",
	tags=["staging"]
    )
}}

with raw_data as (
    select *
    from {{source('raw_data', 'dev_api_data')}}
)

select * from raw_data
