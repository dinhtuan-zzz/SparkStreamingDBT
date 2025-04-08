
  
    
        create table raw_staging.stg_raw
      
      
      
      
      
      
      
      

      as
      

with raw_data as (
    select *
    from raw.dev_api_data
)

select * from raw_data
  