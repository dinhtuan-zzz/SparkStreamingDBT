with staging as (
    select * from {{ ref('stg_raw') }}

)

select	
	id,
	uid,
	first_name,
	last_name, 
	email, 
	gender,
	avatar,
	date_of_birth,
	employment.title,
	address.city,
	address.street_name,
    	address.street_address,
    	address.zip_code,
    	address.state,
    	address.country
from staging


