
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select target_currency
from DE_PORTOFOLIO_DB.RAW_staging.silver_exchange_rates
where target_currency is null



  
  
      
    ) dbt_internal_test