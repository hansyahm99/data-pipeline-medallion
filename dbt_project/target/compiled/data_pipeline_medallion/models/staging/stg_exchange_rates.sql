with source as (

    select * from DE_PORTOFOLIO_DB.RAW.raw_exchange_rates
),

renamed as (
    select
        base_currency,
        target_currency,
        rate::float as rate,
        to_timestamp_tz(rate_date, 'DY, DD MON YYYY HH24:MI:SS TZHTZM')::date as rate_date,
        ingested_at::timestamp_ntz as ingested_at,
        source_file

    from source
)

select * from renamed