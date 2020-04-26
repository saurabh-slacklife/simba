def search_email_template(email: str):
    return {"query": {"match": {"email": {"query": email, "operator": "and"}}}}


def search_contact_number_template(contact_number: str):
    return {"query": {"match": {"contact_number": {"query": contact_number, "operator": "and"}}}}


def search_email_contact_number_template(email: str, contact_number: str):
    return {"query": {"bool": {"must": [{"match": {"contact_number": {"query": contact_number, "operator": "and"}}},
                                        {"match": {"email": {"query": email, "operator": "and"}}}
                                        ]}}}


def search_name_template(name: str):
    return {"query": {"match": {"client_name": {"query": name, "operator": "and"}}}}
