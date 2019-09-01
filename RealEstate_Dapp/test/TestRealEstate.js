var RealEstate = artifacts.require("./RealEstate.sol");

contract('RealEstate', function(accounts){ //accounts라는 인자를 callback으로 받음, 가나슈10계정
    var realEstateInstance; //전역변수 선언
    
    it("컨트랙트 소유자 초기화 테스팅", function() {
        return RealEstate.deployed().then(function(instance){//스마트컨트랙트 인스턴스 받아옴
            realEstateInstance = instance; //인스턴스를 RealEstateInstance 전역변수로 저장
            return realEstateInstance.owner.call();//인스턴스의 상태변수 owner를 콜함
        }).then(function(owner){ //덴을통해 콜백으로 owner값을 받고, assertion을통해 확인
            assert.equal(owner.toUpperCase(), accounts[0].toUpperCase(), "owner가 가나슈 첫번째 계정과 동일하지 않습니다.");
        }); //assertion의 3파라미터는 순서대로, 실제값(리턴값), 예상값(정답값), 두 값이 다를때 출력메세지
        //둘다 대문자쓰는이유는 가나슈계정이 대문자소문자 섞여있어서 동일환경에서 비교하기 위함임
    });
    it("가나슈 두번째 계정으로 매물 아이디 0번 매입 후 이벤트 생성 및 매입자 정보와 buyers 배열 테스팅", function(){
        return RealEstate.deployed().then(function(instance){
            realEstateInstance = instance;
            return realEstateInstance.buyRealEstate(0,"js",13,{from : accounts[1],value:web3.utils.toWei('1.5','ether')});
        }).then(function(receipt){
            assert.equal(receipt.logs.length,1, "이벤트 하나가 생성되지 않았습니다");
            assert.equal(receipt.logs[0].event,"LogBuyRealEstate", "이벤트가 LogBuyRealEstate가 아닙니다.");
            assert.equal(receipt.logs[0].args._buyer, accounts[1], "매입자가 가나슈 두번째 계정이 아닙니다.")
            assert.equal(receipt.logs[0].args._id, 0, "매물 id가 0번이 아닙니다.")
            return realEstateInstance.getBuyerInfo(0);
        }).then(function(buyerInfo) {
            assert.equal(buyerInfo[0].toUpperCase(), accounts[1].toUpperCase(),"매입자의 계정이 가나슈 두번쨰 계쩡과 일치하지 않음"); //주소비교
            //web3.toAscii v5지원x   assert.eqaul(web3.toAscii(buyerInfo[1]).replace(/\0/g,''), "js","매입자의 이름이 js가 아닙니다");//이름비교
            assert.equal(buyerInfo[2],13, "매입자나이 13살이 아님");//나이비교
            return realEstateInstance.getAllBuyers();//getAllBuyer함수 테스트
        }).then(function(buyers){
            assert.equal(buyers[0].toUpperCase(), accounts[1].toUpperCase(), "buyers배열 첫번째 인덱스의 계정이 가나슈 두번째와 일치하지 않음");
             // id 10개에 순서대로, 매입자의 주소가 판매된 부동산번호에 기입되어있는지를 확인하는 것,
             // 예제에서 0번이팔렸으므로, buyer[0] = 구입자의address가 와야함
        });
        })
    })
