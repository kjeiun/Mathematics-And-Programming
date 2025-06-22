import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import time

# 셀레니움 드라이버 생성
driver = webdriver.Chrome()
usr = "kjeiun@yonsei.ac.kr"
pwd = "010525kk!!"

driver.get("https://www.jobplanet.co.kr/users/sign_in?_nav=gb")


login_id = driver.find_element(
    By.CSS_SELECTOR, "body > div.mx-auto.h-auto.w-\[960px\].pb-\[15px\] > div > div.p-\[28px_32px_0\] > section.border-t.border-gray-100.pt-\[20px\].mb-\[30px\] > form > label:nth-child(1) > div > input")
login_id.send_keys(usr)
login_pwd = driver.find_element(
    By.CSS_SELECTOR, "body > div.mx-auto.h-auto.w-\[960px\].pb-\[15px\] > div > div.p-\[28px_32px_0\] > section.border-t.border-gray-100.pt-\[20px\].mb-\[30px\] > form > label:nth-child(2) > div > input")
login_pwd.send_keys(pwd)

login_id.send_keys(Keys.RETURN)


#!! 아래 주석 처리 된 부분은 company list를 받아오는 부분이고, 실제로 xlsx파일은 data부분에 추가되었기 때문에
# read excel으로 불러오는 부분으로 대체하였습니다.
# 실제 코드를 돌리실 때에는 기존에 저장된 company1000.xlsx파일을 이용하셔서 id를 바탕으로 주석처리된 부분은
# 사용하지 않으시고 돌리시면됩니다!!

# # 첫 번째 페이지부터 100페이지까지 순회
# for page_num in range(1, 101):

#     # 모든 페이지에 대해서 회사의 이름과 id 쌍을 얻기
#     # 웹 페이지 열기
#     url = f'https://www.jobplanet.co.kr/companies?sort_by=review_survey_total_avg_cache&page={page_num}'
#     driver.get(url)

#     # 웹 페이지가 로딩될 때까지 기다리기 (예: 5초 기다림)
#     driver.implicitly_wait(5)

#     # HTML 가져오기
#     html = driver.page_source

#     # Beautiful Soup을 사용하여 HTML 파싱
#     soup = BeautifulSoup(html, 'html.parser')

#     # 회사 id와 이름을 가지고 있는 element 찾기
#     a_element = soup.select(
#         '#listCompanies > div > div.section_group > section > div > div > dl.content_col2_3.cominfo > dt > a')

#     print(f'Page {page_num}, len: {len(a_element)}')

#     # 특정 회사의 name 과 id를 company_list 에 넣고 엑셀에 저장
#     for i in range(len(a_element)):
#         company_name = a_element[i].get_text(strip=True)
#         # print(company_name)
#         company_id_href = a_element[i]['href']
#         company_id = company_id_href.split('/')[2]
#         company_list.append(
#             {'Company Name': company_name, 'Company ID': company_id})
#     df = pd.DataFrame(company_list)
#     df.to_excel('Company1000.xlsx', index=False)

# 회사 리스트 불러오기
df = pd.read_excel('Company1000.xlsx')
company_list = df.iloc[700:].to_dict('records')


# 회사 id와 이름 이외에 구체적인 데이터를 담고 있는 리스트
totals = []
count = 700

for company in company_list:
    try:
        count += 1
        print(f"[{count}] {company['Company Name']}")

        company_id = str(company['Company ID'])
        company_name = company['Company Name']

        # 리뷰 페이지 이동 및 로딩 대기
        driver.get(
            f'https://www.jobplanet.co.kr/companies/{company_id}/reviews/')
        WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR,
                                                 'span.txt_point.absolute.left-\\[105\\%\\].top-\\[-5px\\].text-\\[13px\\].text-\\[\\#333\\]'
                                                 ))
        )

        soup = BeautifulSoup(driver.page_source, 'html.parser')
        point_list = soup.select(
            'span.txt_point.absolute.left-\\[105\\%\\].top-\\[-5px\\].text-\\[13px\\].text-\\[\\#333\\]'
        )

        p1 = point_list[0].text.strip()
        p2 = point_list[1].text.strip()
        p3 = point_list[2].text.strip()
        p4 = point_list[3].text.strip()
        p5 = point_list[4].text.strip()

        # 연봉 페이지 이동 및 로딩 대기
        driver.get(
            f'https://www.jobplanet.co.kr/companies/{company_id}/salaries/')
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR,
                                            '#sideContents > div:nth-child(3) > div > div:nth-child(1) > div.txt_rgt > div.num > em'
                                            ))
        )

        soup = BeautifulSoup(driver.page_source, 'html.parser')
        salary = soup.select_one(
            '#sideContents > div:nth-child(3) > div > div:nth-child(1) > div.txt_rgt > div.num > em'
        ).text.strip()

        in_num = soup.select_one(
            '#sideContents > div:nth-child(3) > div > div:nth-child(2) > div.num > em'
        ).text.strip()

        out_num = soup.select_one(
            '#sideContents > div:nth-child(3) > div > div:nth-child(3) > div.num > em'
        ).text.strip()

        totals.append({
            'Company Name': company_name,
            'Company ID': company_id,
            '복지 및 급여': p1,
            '업무와 삶의 균형': p2,
            '사내문화': p3,
            '승진 기회 및 가능성': p4,
            '경영진': p5,
            '연봉': salary,
            '입사자 수': in_num,
            '퇴사자 수': out_num
        })
        print(totals[-1])
    except Exception as e:
        print(f" 에러 in : {company_name}")
        print(f" 원인: {e}")
        salary = in_num = out_num = 'no info'

    if count % 100 == 0:
        df_partial = pd.DataFrame(totals)
        df_partial.to_excel(f'jobPlanetData_{count}.xlsx', index=False)
        print(f"{count}개 데이터 저장")

# 최종 전체 데이터 저장
df = pd.DataFrame(totals)
df.to_excel('jobplanet_data.xlsx', index=False)

# 셀레니움 종료
driver.quit()
