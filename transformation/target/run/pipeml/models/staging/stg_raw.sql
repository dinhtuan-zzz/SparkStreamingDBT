
  
    
        create table raw_staging.stg_raw
      
      
      
      
      
      
      
      

      as
      

with raw_data as (
    select *
    from raw.daily
)

select * from raw_data
  