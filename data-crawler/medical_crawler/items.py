import scrapy


class DrugRawItem(scrapy.Item):
    drug_id = scrapy.Field()
    name = scrapy.Field()
    approval_no = scrapy.Field()
    dosage_form = scrapy.Field()
    spec = scrapy.Field()
    usage = scrapy.Field()
    adverse_reaction = scrapy.Field()
    contraindication_text = scrapy.Field()
    pharmacology_text = scrapy.Field()
    ingredients = scrapy.Field()


class DiseaseRawItem(scrapy.Item):
    disease_id = scrapy.Field()
    name = scrapy.Field()
    icd_code = scrapy.Field()
    aliases = scrapy.Field()
    department = scrapy.Field()
    symptoms = scrapy.Field()
    treatments = scrapy.Field()


class GuidelineRawItem(scrapy.Item):
    chunk_id = scrapy.Field()
    content = scrapy.Field()
    source = scrapy.Field()
    publish_year = scrapy.Field()
    drug_refs = scrapy.Field()
    disease_refs = scrapy.Field()
