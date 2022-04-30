-- debug pruposes only - proceed with caution of course
-- order of deletion matters because of foreign keys

drop table petition;
drop table vignette;
drop table signature_by_constituency;
drop table signature_by_country;
drop table mp;
DROP TABLE debate;
-- don't drop the constituency table; its static

