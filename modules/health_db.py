# [AI 사용 표시]
# AI 종류: ChatGPT
# AI 사용 목적: 모듈 1의 건강정보 클래스와 JSON, TXT 파일 저장·읽기 구현 보조
# 사용한 프롬프트: "BMI 지정프로젝트 요구서의 모듈 1에 맞게
# HealthRecord와 건강정보 관리 클래스를 작성하고 JSON, TXT 파일 저장 및 읽기,
# 원본 데이터와의 일치 검증 코드를 작성해줘."
# 사용한 사람: 김윤빈
# 사용 날짜: 2026-11-16
import csv
import json
from datetime import datetime
from pathlib import Path

class HealthRecode :
    def __init__(self,id,name,birth_year,gender,height,weight,bmi,status):
        self.id = id
        self.name = name
        self.birth_year = birth_year
        self.gender = gender
        self.height = height
        self.weight = weight
        self.bmi = bmi
        self.status = status

    #건강정보를 딕셔너리로 바꿔 반환
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "birth_year": self.birth_year,
            "gender": self.gender,
            "height": self.height,
            "weight": self.weight,
            "bmi": self.bmi,
            "status": self.status
        }
#건강정보 목록을 관리하고 TXT 파일로 저장하는 클래스
class HealthDatabase:
    FIELDS=["id","name","birth_year","gender","height","weight","bmi","status"]

    def __init__(self):
        self.records=[]

    #현재 목록에 없는 식별번호 만들기
    def make_id(self):
        existing_ids={record.id for record in self.records}
        year = datetime.now().year
        number = 1

        while f"p{year}-{number:04d}" in existing_ids:
            number += 1

        return f"p{year}-{number:04d}"
    # 새 건강정보를 만들어 목록에 추가
    def add_record(self, name, birth_year, gender, height, weight, bmi, status):
        record = HealthRecode(
            self.make_id(),name, birth_year, gender, height, weight, bmi, status
        )
        self.records.append(record)
        return record

    #건강정보 목록을 딕셔너리 목록으로 바꾼다
    def get_records_as_dicts(self):
        return [record.to_dict() for record in self.records]

    #건강정보 목록 탭으로 구분한 TXT 파일로 저장한다.
    def save_txt(self, path):
        try:
            with open(path,"w",encoding="utf-8",newline="")as file:
                writer = csv.DictWriter(
                    file,
                    fieldnames=self.FIELDS,
                    delimiter="\t"
                )
                writer.writeheader()
                writer.writerows(self.get_records_as_dicts())

            print("TXT 파일 저장 완료:",path)

        except (OSError, TypeError) as error:
            print("TXT 파일 저장 오류:",error)

    #TXT 파일을 읽어 딕셔너리 목록으로 반환
    def load_txt(self, path):
        try:
            with open(path,"r",encoding="utf-8",newline="") as file:
                reader = csv.DictReader(file, delimiter="\t")
                return [self.convert_row(row) for row in reader]
        except(OSError,ValueError,KeyError) as error:
            print("TXT 파일 읽기 오류:",error)
            return []

    #TXT에서 읽은 값을 원래 숫자 자료형으로 바꾼다
    def convert_row(self, row):
        return {
            "id":row["id"],
            "name":row["name"],
            "birth_year": int(row["birth_year"]),
            "gender": row["gender"],
            "height": float(row["height"]),
            "weight": float(row["weight"]),
            "bmi": float(row["bmi"]),
            "status": row["status"]
        }
    
        #건강 정보 목록을 화면에 출력
    def print_records(self, records, title):
       
        print(f"\n[{title}]")

        for record in records:
            print(record)

def main():
        database = HealthDatabase()

    # 임의의 건강정보 두 건을 추가한다.
        database.add_record(
        "홍길동", 1995, "남",
        175.0, 72.5, 23.67, "과체중"
    )
        database.add_record(
        "김영희", 1998, "여",
        162.0, 52.0, 19.81, "정상"
    )

        # 저장 전 원래 데이터를 보관한다.
        original_records = database.get_records_as_dicts()
        database.print_records(original_records, "저장 전 원본 정보")

        # data 폴더를 만들고 TXT 파일에 저장한다.
        data_folder = Path("data")
        data_folder.mkdir(exist_ok=True)
        txt_path = data_folder / "health_data.txt"

        database.save_txt(txt_path)

        # TXT 파일을 다시 읽는다.
        loaded_records = database.load_txt(txt_path)
        database.print_records(loaded_records, "TXT에서 읽은 정보")

        # 원본과 읽어 온 정보가 같은지 확인한다.
        print("원본과 일치:", loaded_records == original_records)


if __name__ == "__main__":
        main()