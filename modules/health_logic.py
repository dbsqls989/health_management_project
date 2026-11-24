
import statistics
from pathlib import Path
from health_db import HealthDatabase,HealthRecode

class HealthManager:
    def __init__(self,database):
        self.database = database

    # 키와 몸무게로 BMI를 계산한다.
    def calculate_bmi(self, height,weight):
        if height <= 0 or weight <= 0:
            raise ValueError("키와 몸무게는 0보다 커야 합니다.")

        height_meter = height / 100
        return round(weight/(height_meter**2),2)
    #BMI 값에 따라 비만도 상태를 정한다.
    def calculate_status(self, bmi):
        if bmi < 18.5:
            return "저체중"
        elif bmi < 23:
            return "정상"
        elif bmi < 25:
            return "과체중"
        else:
            return "비만"

    #중복을 확인한 뒤 새 건강정보를 추가한다.
    def add_record(self, name, birth_year, gender, height, weight):
        if self.check_duplicate(name, birth_year, gender):
            return None

        bmi = self.calculate_bmi(height, weight)
        status = self.calculate_status(bmi)

        return self.database.add_record(name, birth_year, gender, height, weight, bmi, status)

    #중복 데이터 검사
    def check_duplicate(self, name, birth_year, gender):
        for record in self.database.records:
            if(record.name==name and record.birth_year==birth_year and record.gender == gender):
                return True
        return False

    #전체 건강정보 목록을 반환한다.
    def get_all_records(self):
        return list(self.database.records)

    #식별번호 또는 이름에 검색어가 포함된 레코드를 반환한다. 건강정보 검색
    def search_records(self, keyword):
        keyword = keyword.lower()

        results = []

        for record in self.database.records:
            if(keyword in record.id.lower() or keyword in record.name.lower()):
                results.append(record)
        return results

    #식별번호가 일치하는 건강정보 한 건을 반환한다.
    def find_by_id(self, record_id):
        for record in self.database.records:
            if record.id == record_id:
                return record
        return None

    #키 또는 몸무게를 수정하고 BMI와 상태를 다시 계산한다.
    def update_record(self, record_id, height=None, weight=None):
        record = self.find_by_id(record_id)

        if record is None:
            return False

        new_height = record.height if height is None else height
        new_weight = record.weight if weight is None else weight

        if new_height <= 0 or new_weight <= 0:
            raise ValueError("키와 몸무게는 0보다 커야 합니다.")

        record.height = new_height
        record.weight = new_weight
        record.bmi = self.calculate_bmi(new_height, new_weight)
        record.status = self.calculate_status(record.bmi)

        return True

    # 식별번호가 일치하는 건강정보를 삭제한다.
    def delete_record(self, record_id):
        record = self.find_by_id(record_id)

        if record is None:
            return False

        self.database.records.remove(record)
        return True

    #레코드 수와 키, 몸무게, BMI의 평균 및 표준편차를 반환한다.
    def get_statistics(self):
        records = self.database.records

        if len(records) == 0:
            return {"count":0}

        height = [record.height for record in records]
        weight = [record.weight for record in records]
        bmis = [record.bmi for record in records]

        return {
            "count": len(records),
            "average_height": statistics.mean(height),
            "std_height": statistics.pstdev(height),
            "average_weight": statistics.mean(weight),
            "std_weight": statistics.pstdev(weight),
            "average_bmi": statistics.mean(bmis),
            "std_bmi": statistics.pstdev(bmis)
        }

#모듈 1을 이용해 TXT 파일에서 목록을 읽어온다.
def load_records(database, path):
    if not path.exists():
        return 0

    rows = database.load_txt(path)
    records = []

    for row in rows:
        record = HealthRecode(
            row["id"],
            row["name"],
            row["birth_year"],
            row["gender"],
            row["height"],
            row["weight"],
            row["bmi"],
            row["status"]
        )
        records.append(record)

    database.records = records
    return len(records)

#건강정보 한 건을 화면에 출력한다.
def print_record(record):
    print(f"식별번호: {record.id}")
    print(f"이름: {record.name}")
    print(f"생년: {record.birth_year}")
    print(f"성별: {record.gender}")
    print(f"키: {record.height} cm")
    print(f"몸무게: {record.weight} kg")
    print(f"BMI: {record.bmi}")
    print(f"상태: {record.status}")
    print("-"*30)

# 0보다 큰 실수를 입력받는다.(올바른 숫자를 입력받음)
def input_positive_float(message):
    while True:
        try:
            value = float(input(message))

            if value <= 0:
                print("0보다 큰 숫자를 입력하세요.")
            else:
                return value
        except ValueError:
            print("숫자로 입력하세요.")

def main():
    database = HealthDatabase()
    manager = HealthManager(database)

    # health_logic.py 가 modules 폴더에 있다고 가정.
    data_path = Path(__file__).resolve().parent.parent / "data" / "health_data.txt"
    data_path.parent.mkdir(parents=True, exist_ok=True)

    loaded_count = load_records(database, data_path)
    print(f"TXT 파일에서 {loaded_count}건을 불러왔습니다.")

    while True:
        print("\n-------- 건강정보 관리 시스템 --------")
        print("1. 추가")
        print("2. 목록 조회")
        print("3. 검색 및 상세조회")
        print("4. 수정 및 삭제")
        print("5. 통계 조회")
        print("6. 파일에서 가져오기")
        print("7. 파일로 저장")
        print("8. 종료")

        choice = input("메뉴를 선택하세요: ")

        if choice == "1":
            name = input("이름: ").strip()

            try:
                birth_year = int(input("생년 "))
                gender = input("성별: ").strip()
                height = input_positive_float("키(cm): ")
                weight = input_positive_float("몸무게(kg): ")

                record = manager.add_record(name, birth_year, gender, height, weight)

                if record is None:
                    print("같은 이름, 생년, 성별의 정보가 이미 있습니다.")
                else:
                    print("건강정보를 추가했습니다.")
                    print_record(record)

            except ValueError as error:
                print("입력 오류:", error)

        elif choice == "2":
            records = manager.get_all_records()

            if len(records) == 0:
                print("등록된 건강정보가 없습니다.")
            else:
                for record in records:
                    print_record(record)

        elif choice == "3":
            keyword = input("이름 또는 식별번호를 입력하세요: ")
            results = manager.search_records(keyword)

            if len(results) == 0:
                print("검색 결과가 없습니다.")
            else:
                for record in results:
                    print_record(record)

        elif choice == "4":
            action = input("수정은 1, 삭제는 2를 입력하세요: ")
            record_id = input("식별번호: ").strip()

            if action == "1":
                height_text = input("새 키(cm), 그대로 두려면 Enter: ").strip()
                weight_text = input("새 몸무게(kg), 그대로 두려면 Enter: ").strip()

                try:
                    height = float(height_text) if height_text else None
                    weight = float(weight_text) if weight_text else None

                    if height is None and weight is None:
                        print("수정할 키나 몸무게를 입력하세요.")
                    elif manager.update_record(record_id, height, weight):
                        print("정보를 수정했습니다.")
                    else:
                        print("해당 식별번호를 찾을 수 없습니다.")

                except ValueError as error:
                    print("입력 오류:", error)

            elif action == "2":
                if manager.delete_record(record_id):
                    print("건강정보를 삭제했습니다.")
                else:
                    print("해당 식별번호를 찾을 수 없습니다.")
            else:
                print("잘못된 메뉴입니다.")

        elif choice == "5":
            stats = manager.get_statistics()

            if stats["count"] == 0:
                print("통계를 낼 건강정보가 없습니다.")
            else:
                print("레코드 수:", stats["count"])
                print(f"평균 키: {stats['average_height']:.2f}cm")
                print(f"키 표준편차: {stats['std_height']:.2f}")
                print(f"평균 몸무게: {stats['average_weight']:.2f}kg")
                print(f"몸무게 표준편차: {stats['std_weight']:.2f}")
                print(f"평균 BMI: {stats['average_bmi']:.2f}")
                print(f"BMI 표준편차: {stats['std_bmi']:.2f}")

        elif choice == "6":
            count = load_records(database, data_path)
            print(f"TXT 파일에서 {count}건을 불러왔습니다.")

        elif choice == "7":
            database.save_txt(data_path)

        elif choice == "8":
            print("프로그램을 종료합니다.")
            break

        else:
            print("1부터 8사이의 메뉴를 선택하세요.")
if __name__ == "__main__":
    main()
