pragma solidity ^0.4.24;


//MyContract라는 컨트랙트를 배포하고, student 구조체생성
contract MyContract {
   struct Student {
       string studentName;  //이름,성별,나이의 세가지파라미터 설정
       string gender;
       uint age;
   }
   
   mapping(uint256 => Student) studentInfo; //student 구조체에 매핑하는 studentInfo 선언
   
   //studentId, 이름,성별,나이를 입력변수로 받는 setStudentInfo를 선언.
   //해당 함수에서 studentInfo의 Id를 입력하여, Student의 student에 저장.
   //이름.나이.성별도 같이 저장.
   function setStudentInfo(uint _studentId, string _name, string _gender, uint _age) public {
       Student storage student = studentInfo[_studentId];
       
       student.studentName = _name;
       student.gender = _gender;
       student.age = _age;
   }
   
   
   //getstudentInfo에서 ID를 입력하면 student ID,이름,성별,
   function getStudentInfo(uint256 _studentId) public view returns (string, string, uint) {
       return (studentInfo[_studentId].studentName, studentInfo[_studentId].gender, studentInfo[_studentId].age);
   }
}
