from openai import OpenAI
import json
import pandas as pd
import re
# Point to the local server
client = OpenAI(base_url="http://localhost:1234/v1", api_key="lm-studio")
df = pd.read_excel("output.xlsx")
# Define a class for the real estate object
real_estate_schema = {
    "description": "string",
    "detail": {
        "address": "string",
        "Type": "string",
        "price": "number",
        "area": "number",
    }
}
examples = {
    "description":"Em cần bán căn hộ 04PN, chung cư Indochina Plaza (IPH) Xuân Thủy - Cầu Giấy. Diện tích: 210 m², thiết kế 04PN. Nội thất đầy đủ, khách mua chỉ việc dọn vào ở. Giá: 15.5 tỷ (có thương lượng). Pháp lý: Sổ hồng chính chủ, sở hữu lâu dài, sẵn sang tên.",
    "detail":
    {
        "address": "Căn hộ 04PN, chung cư Indochina Plaza (IPH) Xuân Thủy - Cầu Giấy",
        "Type": "Chung cư",
        "price": "15,5 tỷ",  
        "area": 210,      
    }
}
while True:
    system_message = f"""You are an expert in real estate.
                You are an intelligent text extraction and conversion assistant. Your task is to extract structured information from the given text and convert it into a pure JSON format.
                The JSON should contain only the structured data extracted from t
                he text, with no additional commentary, explanations, or extraneous information.
                1. **Address:** Extract the address, which can be a street or a district, and may include personal names.
                2. **Type:**  "mảnh đất" or "căn hộ" or "subpenhouse".
                3. **Price Calculation:** 
                - Extract the price in VND. Prices may be presented with units like "tỷ" (billion VND), "tr" or "triệu" (million VND).
                - Convert these units to VND:
                    - "tỷ" = 1,000,000,000 VND
                    - "tr" or "triệu" = 1,000,000 VND
                    72tr/m2 is amount_per_m2 and 1.5 tỷ is price.
                price = amount_per_m2(tr/m2) * area
                take a look at this example: {examples}
                4. **Area:** Extract the area in square meters.
                Please ensure that all extracted data is converted to a pure JSON format. In cases where the data is not available or is in a foreign language, handle it appropriately.
                Output only the JSON data with no additional text or explanations. The JSON should include `address`, `type`, `price`, and `area` fields. If the `type` is not specified, default to "căn hộ" (apartment). If the `amount_per_m2` is not specified, calculate it as `price / area`."""
    user_message = input("Description: ")
    
    if user_message.lower() in ["exit", "quit"]:
        break
    else:
        try:
            completion = client.chat.completions.create(
                model="model-identifier",  # Replace with your model identifier
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": user_message}
                ],
                temperature=0.7,
            )
            
            # Extract and print the message from the completion response
            json_str = re.search(r'\{[^}]*\}', completion.choices[0].message.content).group(0)
            json_data = json.loads(json_str)
            new_df = pd.DataFrame([json_data])
            if not df['address'].isin([json_data['address']]).any():
                # Nếu không tồn tại, thêm vào DataFrame
                df = pd.concat([df, new_df], ignore_index=True)


        except Exception as e:
            print(f"An error occurred: {e}")
df.to_excel("output.xlsx", index=False)
