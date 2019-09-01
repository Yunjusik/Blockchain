//solium-disable linebreak-style
pragma solidity >=0.4.21 <0.6.0;

contract RealEstate {
 struct Buyer {
     address buyerAddress;
     string name;
     uint age;
 }
 mapping (uint => Buyer) public buyerInfo;
 address payable public owner; //5.0 solc에서 owner에 payable이 선언되어야 transfer 사용 가능해보임.
 address[10] public buyers;

//event 생성시 이벤트구조 내부 내용도 블록 안에 저장됨.
//매입자가 매입시, 이벤트함수로 공지함
event LogBuyRealEstate(
    address _buyer,
    uint _id
);

  constructor() public {
     owner = msg.sender;
  }

  function buyRealEstate(uint _id, string memory _name, uint _age) public payable {
      require(_id >= 0 && _id <= 9); //ID는 0에서 9사이 (계정)
      buyers[_id] = msg.sender; //buyers[매물번호] = 산사람 주소, 의 형태로 저장이 됨
      buyerInfo[_id] = Buyer(msg.sender, _name, _age); //id,name,age입력받아 Buyer 구조체로 전달
      owner.transfer(msg.value);

      emit LogBuyRealEstate(msg.sender, _id);// 부동산 사고, 송금직후에 이벤트함수 발생시킴.
      //buyRealEstate의 msg.sender는 구매자이므로, 구매자의 주소와 id를 반환하게됨.
  }
 //읽기전용 함수
  function getBuyerInfo(uint _id) public view returns (address, string memory, uint) {
      Buyer memory buyer = buyerInfo[_id];
      return (buyer.buyerAddress, buyer.name, buyer.age);
  }

    function getAllBuyers() public view returns (address[10] memory) {
        return buyers;
    }
}
