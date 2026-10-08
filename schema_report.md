# Schema report: `validate`

19 tables/views.

## alembic_version (base table)

Rows: 1

| column | type | nullable |
|---|---|---|
| version_num | character varying | NO |

Sample rows:

| version_num |
|---|
| e3f8a1c92b47 |

## attributes (base table)

Rows: 0

| column | type | nullable |
|---|---|---|
| id | uuid | NO |
| name | text | NO |
| title | text | YES |
| reference_url | text | YES |
| unit | character varying | YES |
| data_type | character varying | YES |
| created_at | timestamp with time zone | NO |
| updated_at | timestamp with time zone | NO |
| record_id | uuid | NO |

Foreign keys: record_id → validate.records.id

Sample rows:

| id | name | title | reference_url | unit | data_type | created_at | updated_at | record_id |
|---|---|---|---|---|---|---|---|---|

## distributions (base table)

Rows: 46702

| column | type | nullable |
|---|---|---|
| id | uuid | NO |
| name | text | NO |
| format | text | YES |
| access_url | text | YES |
| description | text | YES |
| created_at | timestamp with time zone | NO |
| updated_at | timestamp with time zone | NO |
| record_id | uuid | NO |

Foreign keys: record_id → validate.records.id

Sample rows:

| id | name | format | access_url | description | created_at | updated_at | record_id |
|---|---|---|---|---|---|---|---|
| ab2969f2-0638-4a14-96fe-3a6bc650afb7 | link-0 | link-0 | https%3A%2F%2Fmaps.bonares.de%2Fmapapps%2Fresources%2Fapps%2Fbonares%2Findex.html%3Flang%3Den%26mid%3D0007bad6-848d-4763-9813-d5ed21cde6ee | None | 2026-09-11 08:42:16.705259+00:00 | 2026-09-11 08:42:16.705259+00:00 | eb82294b-adac-4973-b466-7935dfc57f41 |
| 08730e34-f248-458f-8b22-ed9c532e4312 | ecuador-1228-soils_file-land_use_and_forest_types-1-500,000.jpg | WWW:DOWNLOAD-1.0-http--download | https%3A%2F%2Fstorage.googleapis.com%2Ffao-maps-catalog-data%2Fuuid%2F000baa63-b19e-4e52-8378-e7b6f3be1f63%2Fresources%2Fecuador-1228-soils_file-land_use_and_forest_types-1-500%2C000.jpg | None | 2026-09-11 08:42:16.705259+00:00 | 2026-09-11 08:42:16.705259+00:00 | cfa727d2-93ba-46bc-821f-eafdff54b616 |

## organizations (base table)

Rows: 8522

| column | type | nullable |
|---|---|---|
| id | uuid | NO |
| name | text | NO |
| aliases | jsonb | YES |
| phone_number | character varying | YES |
| ror_identifier | character varying | YES |
| street_address | text | YES |
| postal_code | character varying | YES |
| city | character varying | YES |
| state_or_region | character varying | YES |
| country | character varying | YES |
| website_url | text | YES |
| created_at | timestamp with time zone | NO |
| updated_at | timestamp with time zone | NO |

Sample rows:

| id | name | aliases | phone_number | ror_identifier | street_address | postal_code | city | state_or_region | country | website_url | created_at | updated_at |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| dc2f65a4-05fe-4919-9546-3749875dad55 | University of Maribor | None | None | None | None | None | None | None | None | None | 2026-09-11 08:42:02.940218+00:00 | 2026-09-11 08:42:02.940218+00:00 |
| 625bdbe8-1af5-442a-8fed-25dddbcccef6 | Henan University of Technology | None | None | None | None | None | None | None | None | None | 2026-09-11 08:42:02.940218+00:00 | 2026-09-11 08:42:02.940218+00:00 |

## person_organization (base table)

Rows: 0

| column | type | nullable |
|---|---|---|
| id | uuid | NO |
| person_id | uuid | NO |
| organization_id | uuid | NO |
| created_at | timestamp with time zone | NO |
| updated_at | timestamp with time zone | NO |

Foreign keys: organization_id → validate.organizations.id, person_id → validate.persons.id

Sample rows:

| id | person_id | organization_id | created_at | updated_at |
|---|---|---|---|---|

## persons (base table)

Rows: 28734

| column | type | nullable |
|---|---|---|
| id | uuid | NO |
| name | text | NO |
| aliases | jsonb | YES |
| email | character varying | YES |
| orcid | character varying | YES |
| created_at | timestamp with time zone | NO |
| updated_at | timestamp with time zone | NO |

Sample rows:

| id | name | aliases | email | orcid | created_at | updated_at |
|---|---|---|---|---|---|---|
| 9c28a0af-c5ee-4003-b800-daaf6eaeb1ed | Peters, Piet | None | None | None | 2026-09-11 08:42:02.940218+00:00 | 2026-09-11 08:42:02.940218+00:00 |
| a539ca33-c094-4286-aa2f-5820ae46a434 | Anzhelika N. Moiseeva | None | None | None | 2026-09-11 08:42:02.940218+00:00 | 2026-09-11 08:42:02.940218+00:00 |

## projects (base table)

Rows: 520

| column | type | nullable |
|---|---|---|
| id | uuid | NO |
| name | text | NO |
| created_at | timestamp with time zone | NO |
| updated_at | timestamp with time zone | NO |

Sample rows:

| id | name | created_at | updated_at |
|---|---|---|---|
| 8cfe7c33-0b6e-4b13-9601-d67006741610 | FRAGMENT | 2026-09-11 09:14:04.823845+00:00 | 2026-09-11 09:14:04.823845+00:00 |
| 9aaf21c3-7ca7-40fc-b613-b7e09ea49f2a | SOILPROM | 2026-09-11 09:14:04.823845+00:00 | 2026-09-11 09:14:04.823845+00:00 |

## recommendation_events (base table)

Rows: 1004

| column | type | nullable |
|---|---|---|
| id | uuid | NO |
| visitor_id | uuid | NO |
| role | text | NO |
| event_type | text | NO |
| query | text | YES |
| record_id | uuid | YES |
| created_at | timestamp with time zone | NO |
| updated_at | timestamp with time zone | NO |

Foreign keys: record_id → validate.records.id

Sample rows:

| id | visitor_id | role | event_type | query | record_id | created_at | updated_at |
|---|---|---|---|---|---|---|---|
| 42f502f7-2eeb-428b-99b0-7009fc1cc8a2 | d34aabb6-86ae-4731-b5df-1017e6b0afb9 | policy_maker | search | carbon emission policy | None | 2026-09-15 07:17:38.611112+00:00 | 2026-09-15 07:17:38.611112+00:00 |
| 9c073029-5af4-403c-a59f-d536f524d989 | d34aabb6-86ae-4731-b5df-1017e6b0afb9 | policy_maker | search | carbon emission policy | None | 2026-09-15 07:17:39.472552+00:00 | 2026-09-15 07:17:39.472552+00:00 |

## record_organization (base table)

Rows: 50153

| column | type | nullable |
|---|---|---|
| id | uuid | NO |
| record_id | uuid | NO |
| organization_id | uuid | NO |
| created_at | timestamp with time zone | NO |
| updated_at | timestamp with time zone | NO |

Foreign keys: organization_id → validate.organizations.id, record_id → validate.records.id

Sample rows:

| id | record_id | organization_id | created_at | updated_at |
|---|---|---|---|---|
| 614054df-c763-4178-8be8-6e78bfbe88ac | eb82294b-adac-4973-b466-7935dfc57f41 | fab8872a-1c7b-4459-83a0-d31b7726b21b | 2026-09-11 08:42:16.705259+00:00 | 2026-09-11 08:42:16.705259+00:00 |
| 2917530e-a581-4f4e-852c-b7f9eb0d53ee | eb82294b-adac-4973-b466-7935dfc57f41 | b0015ec9-95f6-47ea-b5b6-3c23cb61d3cf | 2026-09-11 08:42:16.705259+00:00 | 2026-09-11 08:42:16.705259+00:00 |

## record_person (base table)

Rows: 61585

| column | type | nullable |
|---|---|---|
| id | uuid | NO |
| record_id | uuid | NO |
| person_id | uuid | NO |
| created_at | timestamp with time zone | NO |
| updated_at | timestamp with time zone | NO |

Foreign keys: person_id → validate.persons.id, record_id → validate.records.id

Sample rows:

| id | record_id | person_id | created_at | updated_at |
|---|---|---|---|---|
| 40ba484c-29d3-41f2-8037-1f5dfba6d3a3 | eb82294b-adac-4973-b466-7935dfc57f41 | 326e29c0-a95d-4fc8-96e1-8a16ea4c8b55 | 2026-09-11 08:42:16.705259+00:00 | 2026-09-11 08:42:16.705259+00:00 |
| c701eb47-db12-4549-8262-c68393178c74 | eb82294b-adac-4973-b466-7935dfc57f41 | 0b1c2776-c177-4c30-be4d-0c261479d0ee | 2026-09-11 08:42:16.705259+00:00 | 2026-09-11 08:42:16.705259+00:00 |

## record_project (base table)

Rows: 6234

| column | type | nullable |
|---|---|---|
| id | uuid | NO |
| record_id | uuid | NO |
| project_id | uuid | NO |
| created_at | timestamp with time zone | NO |
| updated_at | timestamp with time zone | NO |

Foreign keys: project_id → validate.projects.id, record_id → validate.records.id

Sample rows:

| id | record_id | project_id | created_at | updated_at |
|---|---|---|---|---|
| 326a79ec-9143-4e1e-824e-78b54291e5f4 | f3e8a073-7401-4030-b059-f8f63b882486 | 1b2681b4-e49f-4c7a-8d2c-d16eb0c0ea91 | 2026-09-11 09:14:41.120437+00:00 | 2026-09-11 09:14:41.120437+00:00 |
| 577d39d2-14c8-4981-8317-00d524c0c542 | 088cf872-6eaa-4e87-8820-8fa497c865a2 | c16bb4b5-f450-4007-9f6e-47b12195485c | 2026-09-11 09:14:41.120437+00:00 | 2026-09-11 09:14:41.120437+00:00 |

## record_source (base table)

Rows: 27271

| column | type | nullable |
|---|---|---|
| id | uuid | NO |
| record_id | uuid | NO |
| source_id | uuid | NO |
| created_at | timestamp with time zone | NO |
| updated_at | timestamp with time zone | NO |

Foreign keys: record_id → validate.records.id, source_id → validate.sources.id

Sample rows:

| id | record_id | source_id | created_at | updated_at |
|---|---|---|---|---|
| f8552c84-084c-4f9e-aa02-a4f4439d6a7a | eb82294b-adac-4973-b466-7935dfc57f41 | 3a9e97a4-9336-48c4-b5f9-d62542dbcb95 | 2026-09-11 08:42:16.705259+00:00 | 2026-09-11 08:42:16.705259+00:00 |
| 07a844e8-93e7-49b6-924c-82e5eb5ee93c | cfa727d2-93ba-46bc-821f-eafdff54b616 | 019f0dd3-1adc-4a2c-ae76-5700d262e61c | 2026-09-11 08:42:16.705259+00:00 | 2026-09-11 08:42:16.705259+00:00 |

## record_subject (base table)

Rows: 105737

| column | type | nullable |
|---|---|---|
| id | uuid | NO |
| record_id | uuid | NO |
| subject_id | uuid | NO |
| created_at | timestamp with time zone | NO |
| updated_at | timestamp with time zone | NO |

Foreign keys: record_id → validate.records.id, subject_id → validate.subjects.id

Sample rows:

| id | record_id | subject_id | created_at | updated_at |
|---|---|---|---|---|
| a02ebc29-bf7b-42d4-bd7e-fcfe06f10ab1 | cfa727d2-93ba-46bc-821f-eafdff54b616 | 9ee264d3-ea52-4900-8315-e9fa2ee3da3c | 2026-09-11 08:42:16.705259+00:00 | 2026-09-11 08:42:16.705259+00:00 |
| 63b18974-d32a-46b6-8d4f-7e86944f3b57 | cfa727d2-93ba-46bc-821f-eafdff54b616 | 71ade860-8d93-4be5-94ad-e8a48a0008ac | 2026-09-11 08:42:16.705259+00:00 | 2026-09-11 08:42:16.705259+00:00 |

## records (base table)

Rows: 25129

| column | type | nullable |
|---|---|---|
| id | uuid | NO |
| identifier | text | NO |
| title | text | NO |
| abstract | text | YES |
| resource_type | text | YES |
| license | text | YES |
| language | text | YES |
| thumbnail | text | YES |
| publication_date | timestamp with time zone | YES |
| resource_creation_date | timestamp with time zone | YES |
| resource_updated_date | timestamp with time zone | YES |
| harvest_date | timestamp with time zone | YES |
| spatial | text | YES |
| temporal_start | timestamp with time zone | YES |
| temporal_end | timestamp with time zone | YES |
| raw_metadata | jsonb | YES |
| created_at | timestamp with time zone | NO |
| updated_at | timestamp with time zone | NO |
| approval_status | character varying | NO |
| url | text | YES |

Sample rows:

| id | identifier | title | abstract | resource_type | license | language | thumbnail | publication_date | resource_creation_date | resource_updated_date | harvest_date | spatial | temporal_start | temporal_end | raw_metadata | created_at | updated_at | approval_status | url |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 32d554a8-a536-4f91-b67a-d3db15bcd668 | 4DAD2E3D-82BB-46DA-979D-941B599A3089 | Bodenübersichtskarte der Bundesrepublik Deutschland 1:1.000.000 (WMS) | Der Web Map Service (WMS) der BÜK1000 stellt bundesweit die Verbreitung der Böden und deren Vergesellschaftung in einheitlicher Form auf dem Aggregierungsniveau der Leitbodenassoziationen dar. Die Kar… | Dataset | None | German | https://download.bgr.de/bgr/boden/BUEK1000DE/WMS/Vorschaugrafik/BUEK1000DE.png | 1995-01-01 00:00:00+00:00 | 1994-12-01 00:00:00+00:00 | 1994-12-01 00:00:00+00:00 | 2026-06-07 00:00:00+00:00 | POLYGON((5.422 47.02, 15.566 47.02, 15.566 55.069, 5.422 55.069, 5.422 47.02)) | None | None | {'date': '1994-12-01T00:00:00Z', 'type': 'Service', 'links': ['{"url":"https%3A%2F%2Fservices.bgr.de%2Fboden%2Fbuek1000","name":null,"format":"link-1"}', '{"url":"https%3A%2F%2Fservices.bgr.de%2Fwms%2… | 2026-09-11 08:43:47.423242+00:00 | 2026-10-08 05:34:24.691161+00:00 | pending | None |
| f2c5471f-ce11-433e-8e19-be960c454652 | 4db2d9c7-5d60-405f-84bd-2d866559a225 | Transpiration (Office du Niger, Mali - Dekadal - 30m) | The transpiration (T) data component (dekadal, in mm/day) is the actual transpiration of the vegetation canopy. The value of each pixel represents the average daily actual transpiration for that speci… | Other | None | English | https://io.apps.fao.org/geoserver/wms/reflect?layers=WAPOR_2:l3_odn_t_d | 2020-01-01 00:00:00+00:00 | None | 2020-01-01 00:00:00+00:00 | 2024-09-16 00:00:00+00:00 | None | 2009-01-01 00:00:00+00:00 | None | {'date': '2020-01-01T00:00:00Z', 'links': ['{"url":"https%3A%2F%2Fio.apps.fao.org%2Fgeoserver%2Fwms%2FWAPOR_2%2FL3_ODN_T_D%2Fv2%3Fservice%3DWMS%26version%3D1.3.0%26request%3DGetCapabilities","name":"W… | 2026-09-11 08:43:47.423242+00:00 | 2026-09-11 08:43:47.423242+00:00 | pending | None |

## records_backup_20260928_161827 (base table)

Rows: 28028

| column | type | nullable |
|---|---|---|
| id | uuid | YES |
| identifier | text | YES |
| title | text | YES |
| abstract | text | YES |
| resource_type | text | YES |
| license | text | YES |
| language | text | YES |
| thumbnail | text | YES |
| publication_date | timestamp with time zone | YES |
| resource_creation_date | timestamp with time zone | YES |
| resource_updated_date | timestamp with time zone | YES |
| harvest_date | timestamp with time zone | YES |
| spatial | text | YES |
| temporal_start | timestamp with time zone | YES |
| temporal_end | timestamp with time zone | YES |
| raw_metadata | jsonb | YES |
| created_at | timestamp with time zone | YES |
| updated_at | timestamp with time zone | YES |

Sample rows:

| id | identifier | title | abstract | resource_type | license | language | thumbnail | publication_date | resource_creation_date | resource_updated_date | harvest_date | spatial | temporal_start | temporal_end | raw_metadata | created_at | updated_at |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| aff7468e-5205-4013-b4a5-a7abdf4004cf | 04869b29-f7a1-4dc0-9ccb-581fafa88983 | Web Map Service of the dataset 'Vegetation data from field boundaries on outer field borders and around habitat islands on the field' | This Web Map Service includes spatial information used by the dataset 'Vegetation data from field boundaries on outer field borders and around habitat islands on the field' | Service | None | English | None | 2024-02-15 00:00:00+00:00 | 2024-02-15 00:00:00+00:00 | 2024-02-15 00:00:00+00:00 | 2024-06-20 00:00:00+00:00 | POLYGON((13.496 53.205, 14.282 53.205, 14.282 53.437, 13.496 53.437, 13.496 53.205)) | None | None | {'date': '2024-02-15T00:00:00Z', 'type': 'Service', 'links': ['{"url":"https%3A%2F%2Fmaps.bonares.de%2Fmapapps%2Fresources%2Fapps%2Fbonares%2Findex.html%3Flang%3Den%26mid%3D+04869b29-f7a1-4dc0-9ccb-58… | 2026-09-11 08:42:16.705259+00:00 | 2026-09-11 08:42:16.705259+00:00 |
| 346d9b61-f36e-40b9-a32c-6ea74db136ff | 0505186a-3973-17e2-58a9-63696e794a36 | BFD5L_M100 | Feldkapazität des Wurzelraums gemäß Bodenflächendaten Hessen 1:5000 für landwirtschaftliche Nutzflächen (BFD5L) - Die Feldkapazität (FK) bezeichnet den Wassergehalt eines natürlich gelagerten Bodens, … | Dataset | None | German | https://www.hlnug.de/fileadmin/dokumente/boden/BFD5L/methoden/img/karte100.png | None | None | None | 2024-09-10 00:00:00+00:00 | POLYGON((7.776 49.396, 10.227 49.396, 10.227 51.657, 7.776 51.657, 7.776 49.396)) | 2023-09-01 00:00:00+00:00 | 2023-09-01 00:00:00+00:00 | {'type': 'Dataset', 'links': ['{"url":"https%3A%2F%2Fgeodienste-umwelt.hessen.de%2Finspire%2FBoden_Hessen%2FBFD5L%2FBFD5L_M100__epsg25832.zip","name":null,"format":"link-0"}'], 'title': 'BFD5L_M100', … | 2026-09-11 08:42:16.705259+00:00 | 2026-09-11 08:42:16.705259+00:00 |

## records_backup_neither_unres_20261008_103426 (base table)

Rows: 25129

| column | type | nullable |
|---|---|---|
| id | uuid | YES |
| identifier | text | YES |
| title | text | YES |
| abstract | text | YES |
| resource_type | text | YES |
| license | text | YES |
| language | text | YES |
| thumbnail | text | YES |
| publication_date | timestamp with time zone | YES |
| resource_creation_date | timestamp with time zone | YES |
| resource_updated_date | timestamp with time zone | YES |
| harvest_date | timestamp with time zone | YES |
| spatial | text | YES |
| temporal_start | timestamp with time zone | YES |
| temporal_end | timestamp with time zone | YES |
| raw_metadata | jsonb | YES |
| created_at | timestamp with time zone | YES |
| updated_at | timestamp with time zone | YES |
| approval_status | character varying | YES |
| url | text | YES |

Sample rows:

| id | identifier | title | abstract | resource_type | license | language | thumbnail | publication_date | resource_creation_date | resource_updated_date | harvest_date | spatial | temporal_start | temporal_end | raw_metadata | created_at | updated_at | approval_status | url |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 4b5d6c14-8589-4449-af86-df3b880fba8e | copernicus_hrl-imperviousness_s,DAT-14-en | HRL Imperviousness | The High Resolution Layer Imperviousness product maps the spatial distribution and dynamics of artificially sealed and built-up areas across Europe. It includes two main datasets: Imperviousness Densi… | Dataset | None | English | https://sdi.eea.europa.eu/public/catalogue-graphic-overview/e3284161-abef-4a2e-a291-cd8ce1cab54e.png | 2026-05-01 00:00:00+00:00 | None | 2026-05-01 00:00:00+00:00 | 2026-06-14 00:00:00+00:00 | POLYGON((-10.62 34.562, 44.821 34.562, 44.821 71.186, -10.62 71.186, -10.62 34.562)) | 2005-01-01 00:00:00+00:00 | 2007-12-31 00:00:00+00:00 | {'date': '2026-05-01T00:00:00Z', 'type': 'Dataset', 'title': 'HRL Imperviousness', 'license': '', 'sources': ['eea'], 'spatial': 'POLYGON((-10.62 34.562, 44.821 34.562, 44.821 71.186, -10.62 71.186, -… | 2026-09-11 08:43:59.016770+00:00 | 2026-09-11 08:43:59.016770+00:00 | pending | https://sdi.eea.europa.eu/catalogue/srv/eng/catalog.search#/metadata/e3284161-abef-4a2e-a291-cd8ce1cab54e |
| 73711447-712c-4b1f-ad5e-1fda8ee0d95e | eea_v_4258_100_k_impervious-area-city_p_2015_v01_r00 | Percentage of impervious areas in core cities (2015), Jan. 2019 | This data shows the information on the percentage of impervious areas in core cities in Europe.  The area of soil sealing is taken from the Copernicus pan-European soil-sealing layer 2015. The referen… | Dataset | None | English | https://sdi.eea.europa.eu/public/catalogue-graphic-overview/45be3406-c677-4b36-8f91-7d3bd5e8a520.png | 2019-01-18 00:00:00+00:00 | 2018-12-19 00:00:00+00:00 | 2018-12-19 00:00:00+00:00 | 2026-03-29 00:00:00+00:00 | POLYGON((-21.68 28.97, 33.38 28.97, 33.38 69.64, -21.68 69.64, -21.68 28.97)) | 2015-01-01 00:00:00+00:00 | 2015-12-31 00:00:00+00:00 | {'date': '2018-12-19T00:00:00Z', 'type': 'Dataset', 'links': ['{"url":"https%3A%2F%2Fclimate-adapt.eea.europa.eu%2Fen%2Fknowledge%2Ftools%2Furban-adaptation","name":null,"format":"WWW:LINK-1.0-http--l… | 2026-09-11 08:43:59.016770+00:00 | 2026-09-11 08:43:59.016770+00:00 | pending | https://sdi.eea.europa.eu/catalogue/srv/eng/catalog.search#/metadata/45be3406-c677-4b36-8f91-7d3bd5e8a520 |

## records_backup_ogc_types_20261007_152216 (base table)

Rows: 25129

| column | type | nullable |
|---|---|---|
| id | uuid | YES |
| identifier | text | YES |
| title | text | YES |
| abstract | text | YES |
| resource_type | text | YES |
| license | text | YES |
| language | text | YES |
| thumbnail | text | YES |
| publication_date | timestamp with time zone | YES |
| resource_creation_date | timestamp with time zone | YES |
| resource_updated_date | timestamp with time zone | YES |
| harvest_date | timestamp with time zone | YES |
| spatial | text | YES |
| temporal_start | timestamp with time zone | YES |
| temporal_end | timestamp with time zone | YES |
| raw_metadata | jsonb | YES |
| created_at | timestamp with time zone | YES |
| updated_at | timestamp with time zone | YES |
| approval_status | character varying | YES |
| url | text | YES |

Sample rows:

| id | identifier | title | abstract | resource_type | license | language | thumbnail | publication_date | resource_creation_date | resource_updated_date | harvest_date | spatial | temporal_start | temporal_end | raw_metadata | created_at | updated_at | approval_status | url |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 088cf872-6eaa-4e87-8820-8fa497c865a2 | 10.1016/j.geoderma.2015.04.019 | Application of smoothed particle hydrodynamics (SPH) and pore morphologic model to predict saturated water conductivity from X-ray CT imaging in a silty loam Cambisol | 20 This study aims to estimate saturated hydraulic conductivity in a silty loam soil and compare modelled data with 21 experimental ones. The flow characteristics of twelve undisturbed soil cores (5 c… | Journal Article | Elsevier TDM | English | None | 2015-10-01 00:00:00+00:00 | None | 2015-10-01 00:00:00+00:00 | None | None | None | None | {'date': '2015-10-01T00:00:00Z', 'type': 'Journal Article', 'title': 'Application of smoothed particle hydrodynamics (SPH) and pore morphologic model to predict saturated water conductivity from X-ray… | 2026-09-11 08:42:16.705259+00:00 | 2026-09-11 08:42:16.705259+00:00 | pending | https://doi.org/10.1016/j.geoderma.2015.04.019 |
| 08928c65-d72d-4f04-b64b-055b39beff1f | 10.1007/s11104-025-07766-z | Deciphering spatiotemporal patterns of rhizodeposition with a functional-structural root model: RhizoDep | Abstract Background and Aims Rhizodeposition, i.e. the release of organic matters by roots, constitutes a significant fraction of the plant carbon (C) budget and plays a key role in plant-soil interac… | Journal Article | CC BY | English | None | 2025-04-03 00:00:00+00:00 | None | 2025-04-03 00:00:00+00:00 | None | None | None | None | {'date': '2025-04-03T00:00:00Z', 'type': 'Journal Article', 'title': 'Deciphering spatiotemporal patterns of rhizodeposition with a functional-structural root model: RhizoDep', 'license': 'CC BY', 'so… | 2026-09-11 08:42:16.705259+00:00 | 2026-09-11 08:42:16.705259+00:00 | pending | https://doi.org/10.1007/s11104-025-07766-z |

## sources (base table)

Rows: 14

| column | type | nullable |
|---|---|---|
| id | uuid | NO |
| name | text | NO |
| description | text | YES |
| created_at | timestamp with time zone | NO |
| updated_at | timestamp with time zone | NO |

Sample rows:

| id | name | description | created_at | updated_at |
|---|---|---|---|---|
| b1dc1b4c-b172-4211-996f-69bde1f0d48a | impact4soil | None | 2026-09-11 08:42:02.940218+00:00 | 2026-09-11 08:42:02.940218+00:00 |
| 1eaca6cb-d9a1-492c-b3db-572f2dc1f2ff | cordis | None | 2026-09-11 08:42:02.940218+00:00 | 2026-09-11 08:42:02.940218+00:00 |

## subjects (base table)

Rows: 20147

| column | type | nullable |
|---|---|---|
| id | uuid | NO |
| uri | text | YES |
| label | text | NO |
| vocabulary_name | text | YES |
| vocabulary_url | text | YES |
| created_at | timestamp with time zone | NO |
| updated_at | timestamp with time zone | NO |

Sample rows:

| id | uri | label | vocabulary_name | vocabulary_url | created_at | updated_at |
|---|---|---|---|---|---|---|
| a7629e48-b795-4dcc-8bd6-a9d03b11eae0 | None | soil micropore | None | None | 2026-09-11 08:42:02.940218+00:00 | 2026-09-11 08:42:02.940218+00:00 |
| 79bceb5b-a7c7-43ed-8253-9dd955953009 | None | pcb, flavonoids, rhizoremediation, chemotaxis | None | None | 2026-09-11 08:42:02.940218+00:00 | 2026-09-11 08:42:02.940218+00:00 |
