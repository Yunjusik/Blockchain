//solium-disable linebreak-style
//original version of source code is from inflearn lecture, (https://www.inflearn.com/course/blockchain-%EC%9D%B4%EB%8D%94%EB%A6%AC%EC%9B%80-dapp#)
//This version has been modified from the original to run Solidity 0.5+ and Truffle v5 +.

pragma solidity >=0.4.21 <0.6.0;

contract RealEstate {
 struct Buyer {
     address buyerAddress;
     string name;
     uint age;
 }
 mapping (uint => Buyer) public buyerInfo;
 address payable public owner; 
 address[10] public buyers;

//when event occurs, structure of event is also saved in block 
//when buyer buys real estate, notice to event log 
event LogBuyRealEstate(
    address _buyer,
    uint _id
);

  constructor() public {
     owner = msg.sender;
  }

  function buyRealEstate(uint _id, string memory _name, uint _age) public payable {
      require(_id >= 0 && _id <= 9); //ID is in range of [0~9]
      buyers[_id] = msg.sender; 
      buyerInfo[_id] = Buyer(msg.sender, _name, _age); //receive id,name,age instance and transfer to Buyer structure
      owner.transfer(msg.value);
      emit LogBuyRealEstate(msg.sender, _id);// emit event log
      //buyRealEstate is buyer of msg.sender, return address &id of buyer
  }
 //read-only function
  function getBuyerInfo(uint _id) public view returns (address, string memory, uint) {
      Buyer memory buyer = buyerInfo[_id];
      return (buyer.buyerAddress, buyer.name, buyer.age);
  }

    function getAllBuyers() public view returns (address[10] memory) {
        return buyers;
    }
}
