import requests

cookies = {
    'BIDUPSID': '455E2872EDCF39EC6BC342028FED7969',
    'PSTM': '1726293841',
    'BAIDUID': '455E2872EDCF39EC920B10A3082F3DF1:FG=1',
    'BAIDUID_BFESS': '455E2872EDCF39EC920B10A3082F3DF1:FG=1',
    'ZFY': 'LA75KkVVTMnAjMJme3ih5BXiGa7TsW9ZtxLjpzex:BYU:C',
    'BD_UPN': '12314753',
    'COOKIE_SESSION': '0_0_1_1_1_2_1_0_1_1_1_0_0_0_6_0_1738822610_0_1738822604%7C1%230_0_1738822604%7C1',
    '__sec_t_key': 'fc0ab9ea-6b4c-469d-9d9e-2866aaf3ff6f',
    'H_PS_PSSID': '60273_61027_62056_62063_62114_62130_62167_62176_62184_62187_62181_62197_62203',
    'BD_HOME': '1',
    'BA_HECTOR': 'a001848g250ga4al0h0g00809i7f791jravhb1u',
}

headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'Accept-Language': 'zh-CN,zh;q=0.9',
    'Cache-Control': 'no-cache',
    'Connection': 'keep-alive',
    'Pragma': 'no-cache',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'none',
    'Sec-Fetch-User': '?1',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36',
    'sec-ch-ua': '"Not(A:Brand";v="99", "Google Chrome";v="133", "Chromium";v="133"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    # 'Cookie': 'BIDUPSID=455E2872EDCF39EC6BC342028FED7969; PSTM=1726293841; BAIDUID=455E2872EDCF39EC920B10A3082F3DF1:FG=1; BAIDUID_BFESS=455E2872EDCF39EC920B10A3082F3DF1:FG=1; ZFY=LA75KkVVTMnAjMJme3ih5BXiGa7TsW9ZtxLjpzex:BYU:C; BD_UPN=12314753; COOKIE_SESSION=0_0_1_1_1_2_1_0_1_1_1_0_0_0_6_0_1738822610_0_1738822604%7C1%230_0_1738822604%7C1; __sec_t_key=fc0ab9ea-6b4c-469d-9d9e-2866aaf3ff6f; H_PS_PSSID=60273_61027_62056_62063_62114_62130_62167_62176_62184_62187_62181_62197_62203; BD_HOME=1; BA_HECTOR=a001848g250ga4al0h0g00809i7f791jravhb1u',
}

response = requests.get('https://censlighting.com/', cookies=cookies, headers=headers)
print(response.text)

