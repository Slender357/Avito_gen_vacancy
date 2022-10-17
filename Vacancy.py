from partools import get_sheet_values2, grv, grv2, CONFIG, get_sheet_values, get_html_strong, get_emoji
import random
from datetime import datetime
import json


class Vacancy:
    def __init__(self, sity: bool, geo: str, reg: bool = False):
        if sity:
            if reg:
                raise BaseException
        self.meta_data = {}
        self.age_preferences = ["olderThan45"]
        self.billing_type = "package"
        self.business_area = 21
        self.description = self.get_description(sity)
        self.experience = "moreThan1"
        self.location = self.get_location(geo, sity, reg)
        self.contacts = self.get_contacts(sity)
        self.programs = self.get_programs()
        self.salary = self.get_salary()
        self.schedule = "flyInFlyOut"
        self.title = self.get_title()
        self.image_url = self.get_image_url()

    def get_description(self, reg):
        sheet_name = CONFIG["sheet_name_m_mo"] if not reg else CONFIG['sheet_name_reg']
        data = get_sheet_values2(sheet_name)
        strong, strong_end, status_strong = get_html_strong()
        title_em, bests_em, adress_em, status_emoji = get_emoji()
        description = f"<p>{strong}{title_em}{grv(data['Заголовок'])}{strong_end}</p>\n" \
                      f"<p>{grv(data['Направление'])}</p>\n" \
                      f"<p>{strong}{grv(data['Оплата'])}{strong_end}</p>\n" \
                      f"<p>{grv(data['Машины'])}</p>\n" \
                      f"<p>{grv(data['Вид машин'])}</p>\n" \
                      f"<p>{bests_em}{grv(data['Преимущества осн1'])}</p>\n" \
                      f"<p>{bests_em}{grv(data['Преимущества осн2'])}</p>\n" \
                      f"<p>{bests_em}{grv(data['Преимущества осн3'])}</p>\n" \
                      f"<p>{bests_em}{grv(data['Преимущества осн4'])}</p>\n" \
                      f"{grv2(data['Преимущества доп'])}" \
                      f"<p>{strong}{adress_em}{grv(data['Адрес'])}{strong_end}</p>"
        self.meta_data['description'] = description
        self.meta_data['strong'] = status_strong
        self.meta_data['emoji'] = status_emoji
        return description

    def get_location(self, geo, sity, reg):
        if sity:
            sheet_name = CONFIG['sheet_name_loction_m']
        else:
            sheet_name = CONFIG['sheet_name_loction_reg'] if reg else CONFIG['sheet_name_loction_mo']
        data = get_sheet_values(sheet_name)
        location = list(data[0].keys())[0]
        metro_dict = {}
        for i in data:
            metro_dict[i[location]] = [k for k in i.values() if k != i[location]]
        location = {
            "coordinates": {
                "latitude": float(str(metro_dict[geo][0]) + str(random.randint(0000, 9999))),
                "longitude": float(str(metro_dict[geo][1]) + str(random.randint(0000, 9999)))
            }
        }
        return location

    def get_contacts(self, sity: bool):
        phone = CONFIG['sity_number'] if sity else CONFIG['region_number']
        name = CONFIG['sity_name'] if sity else CONFIG['region_name']
        contacts = {
            "allow_messages": False,
            "name": name,
            "phone": phone
        }
        self.meta_data['phone'] = phone
        return contacts

    def get_salary(self):
        data = get_sheet_values(CONFIG['sheet_name_salary'])
        salary = random.sample(data, 1)[0]
        finaly_salary = {}
        for i, k in salary.items():
            if k == '':
                continue
            finaly_salary[i] = int(k)
        return finaly_salary

    def get_title(self):
        data = get_sheet_values(CONFIG['sheet_name_title'])
        t_title = list(data[0].keys())[0]
        return random.sample(data, 1)[0][t_title]

    def get_programs(self):
        programs = [
            "chastyeVyplaty"
        ]
        return programs

    def get_image_url(self):
        key = random.sample(list(CONFIG['sheet_name_image_id'].keys()), 1)[0]
        data = get_sheet_values(CONFIG['sheet_name_image_id'][key])
        url = list(data[random.randint(0, len(data) - 1)].values())[0]
        self.meta_data['image_type'] = key
        return f'https://drive.google.com/uc?export=view&id={url}'

    def get_json(self):
        params = {
            "age_preferences": self.age_preferences,
            "billing_type": self.billing_type,
            "business_area": self.business_area,
            "contacts": self.contacts,
            "description": self.description,
            "experience": self.experience,
            "location": self.location,
            "programs": self.programs,
            "salary": self.salary,
            "schedule": self.schedule,
            "title": self.title,
            "image_url": self.image_url
        }
        self.meta_data['title'] = self.title
        salary_to_data = ''
        for i in self.salary.keys():
            salary_to_data += i
        self.meta_data['salary'] = salary_to_data
        return params, self.meta_data


if __name__ == "__main__":
    vacancy = Vacancy(sity=False, geo='Архангельск', reg=True)
    params, meta_data = vacancy.get_json()
    print(meta_data)
