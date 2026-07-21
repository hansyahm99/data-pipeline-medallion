
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select rate_date
from DE_PORTOFOLIO_DB.RAW_staging.silver_exchange_rates
where rate_date is null



  
  
      
    ) dbt_internal_test