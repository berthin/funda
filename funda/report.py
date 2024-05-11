from funda.markdown import MarkdownDocument

import pandas as pd
from pandas.core.series import Series


def to_markdown(listing: Series) -> None:
    md = MarkdownDocument()

    basic_info_fields = ["url", "address", "zip_code", "neighborhood_name"]
    property_details_fields = ["size", "living_area", "year", "kind_of_house", "building_type", "num_of_rooms", "num_of_bathrooms", "energy_label", "insulation", "heating", "ownership"]
    listing_details_fields = ["price", "listed_since", "date_list", "last_ask_price", "last_ask_price_m2"]
    additional_info_fields = [
        "descrip",
        "layout", "exteriors", "parking", "date_sold", "term", "price_sold", 
        #"photo",
    ]

    # Basic Information
    md.append_heading('Basic Information')
    for field in basic_info_fields:
        md.append_bullet(f'**{field.capitalize()}:** {listing[field]}')

    # Property Details
    md.append_heading('Property Details')
    for field in property_details_fields:
        md.append_bullet(f'**{field.capitalize()}:** {listing[field]}')

    # Listing Details
    md.append_heading('Listing Details')
    for field in listing_details_fields:
        md.append_bullet(f'**{field.capitalize()}:** {listing[field]}')

    # Additional Information
    md.append_heading('Additional Information')
    for field in additional_info_fields:
        md.append_bullet(f'**{field.capitalize()}:** {listing[field]}')

    return md