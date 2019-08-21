**Truffle migration by ganache-gui**
현재 인터넷이나 강좌등 대부분이 Truffle 사용을 V4기준, web 1.0 미만버전에서 사용중
트랜잭션 배포, 기타 자잘한 web명령어 바뀐부분들을 정리



가나슈 gui 실행후, trufle.js 파일 주소를 가나슈와 연동
접속 명령어 :
1. Truffle migrate --network ganache  
2. Truffle console
3. in console ) migrate --compile-all --reset
=>현재 sol파일을 가나슈네트워크에 배포. 현재 ganache quicstart 기준 주소가 7545이므로, truffle.js 주소7545로 설정

Truffle console
-> 현재 트러플.js 환경설정의 네트워크로 접속 (develop로 새로만들지 않음)

-----------콘솔 명령어--------------------

v4에서는 컨트랙트명.deployed().then(function(instance){ app = instance"})
app.함수이름(내용)~ 식으로 작성 가능


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

**기본꼴: instance.setStudentInfo(1515,"name","male", 28)**

**노드 지정:  instance.setStudentInfo(1212, "name2", "male", 33, {from: accounts[1]}) ->0번노드가 아닌 1번에서 처리**

**등록정보 불러오기: instance.getStudentInfo(1212) -> name2 반환, (1212대신 1515쓰면 name반환)**

-------------부동산 Dapp------------------
contract 소유자 계정에 돈을 송금/ owner = msg.sender. ganache 첫계정 owner.

instance.owner.call() -> msg.sender 주소 반환

truffle test --network ganache
-현 test폴더 내 js파일에 쓰여진대로 test스크립트를 실행하고 결과 리턴

매물구입함수. 
prerequsite - account는 let accounts로 바꿔놓고 시작하는게 편함
let accounts = await web.eth.getAccounts(),   ex) accounts[1] = 맨위노드주소 반환

instance.buyRealEstate(0,"js", 28, {from:accounts[1], value:web3.utils.toWei('1.50', 'ether')})
-> 매물은 0 ~ 9까지있고, 0번구입을위해 1.5 이더 지불하고, 구매자는 2번째노드. 
-> V4기준 web3.toWei가 아닌 web3.utils.toWei를 사용하고, 양 끝 기호가 "->'로 바뀜.
-> 기존 Dapp 레퍼런스는 bytes32를 사용하는데, 현재 리믹스 등 기타 다른 컴파일러에서도 bytes32 대신 string을 사용할 것... 단 string 사용시 string memory로 


<event 함수>
truffle v4에서는 watch 지원되지만, v5에서는 watch 사라짐.
event를 받아보기위해 사용하는 watch 는 https://web3js.readthedocs.io/en/v1.2.0/web3-eth-contract.html#event
사이트에서 확인해 볼 수 있으나, 현재 ganache 및 트러플에서는 제대로 사용이 안되는걸로 보임

매입자 정보 불러오기
instance.getBuyerInfo(0);
instance.getAllbuyers();

대신에 getPastEvents함수를 사용해서 이전블록에 담긴 이벤트를 확인해 볼 순 있음.
코드: instance.getPastEvents('LogBuyRealEstate',{},{fromBlock:0,toBlock:'latest'},function(error,events){console.log(events);}).then(function(events){console.log(events)});

