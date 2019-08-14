**Truffle migration by ganache-gui**

준비물 : 가나슈 gui 실행후, trufle.js 파일 주소를 가나슈와 연동

Truffle console
-> 현재 트러플.js 환경설정의 네트워크로 접속 (develop로 새로만들지 않음)

-----------콘솔 명령어--------------------
web3.eth.getAccounts() 
->현재 네트워크 계정주소 반환

let instance = await 컨트랙트이름.deployed()
-> 해당 컨트랙트를 디플로이하고, instance라는 변수로 새지정.

**await는 simpe smart contract interaction을 위해 사용**

let accounts = await web3.eth.getAccounts()
-> 현재 가나슈 계정정보를 accounts로 지정

let balance = await instance.getBalance(accounts[0])
-> 현재 잔액내용을 balance로 지정


instance.함수('내용')
-> 해당 컨트랙트 내 '함수'를 '내용'만큼 실행
-> 해당 함수를 실행시키는 주체를 정해주지 않으면, 기본적으로 1번노드 (account[0])이 트랜잭션을 발행함.


web3.eth.
-------------------------------



