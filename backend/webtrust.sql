show databases;
create database webtrust;
use webtrust;

create table ads(document_id integer, ad_count integer, ad_max_size integer);

insert into ads values (2199427,4,75000);

select * from ads;