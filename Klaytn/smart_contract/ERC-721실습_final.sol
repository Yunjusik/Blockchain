// Klaytn IDE uses solidity 0.4.24, 0.5.6 versions.
//external -> public으로 바꿔서 적용, 함수간 상호참조 가능하도록
// payable 제거. 
//인터페이스
pragma solidity >=0.4.24 <=0.5.6;

interface ERC721 /* is ERC165 */ {

    event Transfer(address indexed _from, address indexed _to, uint256 indexed _tokenId);
    event Approval(address indexed _owner, address indexed _approved, uint256 indexed _tokenId);
    event ApprovalForAll(address indexed _owner, address indexed _operator, bool _approved);

    function balanceOf(address _owner) public view returns (uint256);
    function ownerOf(uint256 _tokenId) public view returns (address);
    function safeTransferFrom(address _from, address _to, uint256 _tokenId, bytes data) public;
    function safeTransferFrom(address _from, address _to, uint256 _tokenId) public;
    function transferFrom(address _from, address _to, uint256 _tokenId) public;
    function approve(address _approved, uint256 _tokenId) public; //토큰 승인, 특정 tokenID에 해당하는 토큰 대신처리
    function setApprovalForAll(address _operator, bool _approved) public;
    //특정 계정이 가진 모든 tokenID를 상대방에게 모두 권한위임할때 사용
    function getApproved(uint256 _tokenId) public view returns (address);
    function isApprovedForAll(address _owner, address _operator) public view returns (bool);
}

interface ERC721TokenReceiver {
    //operator주소, from주소, 토큰id, _data 값을 모아 keccak256때린 해시값의 4bytes만 짤라낸값을 리턴
    //EIP에서 이를 magic value라고 한다
    function onERC721Received(address _operator, address _from, uint256 _tokenId, bytes _data) public returns(bytes4);
}

interface ERC165 {
    function supportsInterface(bytes4 interfaceID) public view returns (bool);
    
}




contract ERC721Implementation is ERC721 {//위 interface안 함수를 모두 구현
    
    mapping (uint256=>address) tokenOwner; //토큰의 id를 키값으로 계정을 리턴하는 mapping. 계정번호 입력시 계정의 주소 리턴
    mapping (address => uint256) ownedTokensCount; //주소를 key로, value를 리턴하는 mapping, 계정주소입력시 토큰의갯수 리턴해줌
    mapping (uint256 => address) tokenApprovals; //tokenId를 키값으로해서 계정 주소를 저장
    mapping (address => mapping (address => bool)) operatorApprovals;
    //누가(address) 누구에게 권한부여를 했는가
    mapping (bytes4 => bool) supportedInterfaces;
    //bytes4값을 키값으로하고 bool 리턴. 외부에서 이 매핑을 통해 ERC721Implementation이 특정 인터페이스 쓰는지 안쓰는지 확인
    
    constructor() public {
        supportedInterfaces[0x80ac58cd]=true; //erc721 interface식별자임
    }
    
    
    function mint(address _to,uint _tokenId) public { //mint-발행하다. 매개변수로 계정주소와 토큰 ID를 받음. _to는 발행된 토큰을 누가 소유할지. 
    //tokenId는 1부터시작해서 1씩 차례대로 증가함
    //1. 매개변수로 넘어온 토큰ID를 to계정이 소유.
    //2. to 계정이 가지고있는 토큰의 전체 갯수를 하나 더 증가시킴
        tokenOwner[_tokenId] = _to; //tokenId(int꼴 인덱스)를 key로 받아와서, tokenOwner에 넣고 그 값을 _to 주소에 매핑
    //tokenId의 주인은 _to
        ownedTokensCount[_to] += 1;
    }
    function balanceOf(address _owner) public view returns (uint256) { //address받아서 value 리턴. 주소의 잔고 토큰 개수 리턴.
        return ownedTokensCount[_owner];
    }
    
    function ownerOf(uint256 _tokenId) public view returns (address){ //value 받고 address 리턴, 
    return tokenOwner[_tokenId]; //tokenId 넣고 address 반환
    }
    
    function transferFrom(address _from, address _to, uint256 _tokenId) public {
    //목적 : 토큰id를 소유하는 from계정에서 ~ _to 계정으로 옮기겠다.
    //유효성 검사 (계정 확인)
        address owner = ownerOf(_tokenId);
        require(msg.sender == owner || getApproved(_tokenId)==msg.sender || isApprovedForAll(owner, msg.sender)); 
        //첫번째 유효성 검사에서 msg.sender는 함수를 호출하는 계정임.
        //getApproved에서 리턴하는 계정이 msg.sender여야함
        // owner계정과 함수를 호출하는 msg.sender인자로 넘겨서, msg.sender가 owner 토큰의 전송권한 있는지 확인, 
        //이때 tokenID는 안넘김. -> 모든 토큰의 권한을 받음
        //위 3가지 조건중 하나만 충족해도 통과됨.
        //1)msg.sender가 owner이거나, 2)해당 토큰ID를 msg.sender가 승인받았거나, 3)소유자의 전체토큰에 대한 접근권을 얻었거나
        require(_from != address(0)); //address(0) ->비어있다의미.
        require(_to != address(0)); // 즉 from과 to의 값이 비어있지 않는것이 요구조건
    
    ownedTokensCount[_from] -= 1;
    tokenOwner[_tokenId] = address(0); //해당 토큰ID 에 대한 소유권을 삭제
    
    ownedTokensCount[_to]    +=1;
    tokenOwner[_tokenId] = _to; //_to 계정이 새로운 토큰의 소유자
    }
    
    function safeTransferFrom(address _from, address _to, uint256 _tokenId) public {
        transferFrom(_from, _to, _tokenId);
        //
        if (isContract(_to)){  //_to 주소가 contract 계정인지 확인
            //스마트컨트랙트 계정이 토큰을 받을수 있는지 없는지 확인해야함
            bytes4 returnValue = ERC721TokenReceiver(_to).onERC721Received(msg.sender, _from, _tokenId, '');
            //_to 계정이 스마트컨트랙트 주소이고, 해당 주소에 ERC721TokenReceiver, 즉 토큰을 수신할 수 있는 계정이고,
            //그리고 그 안에있는 msg.sender,from,tokenid 값을 넘겨 keccak256 한 값(magic value) returnvalue에 넣는다. 
            //즉 magic value가 returnvalue로 나오는지 확인하는것임.
            require(returnValue == 0x150b7a02);
            //erc721 토큰 리시버 식별자 0x150b7a02
        }
    }
    
    function safeTransferFrom(address _from, address _to, uint256 _tokenId, bytes data) public {
        transferFrom(_from, _to, _tokenId);
        
        if (isContract(_to)){  
            bytes4 returnValue = ERC721TokenReceiver(_to).onERC721Received(msg.sender, _from, _tokenId, data);
        
        }
    }
    function approve(address _approved, uint256 _tokenId) public {//전송권한 부여
        address owner = ownerOf(_tokenId);
        require(_approved != owner);
        require(msg.sender == owner); //함수호출계정이 함수의 소유자
        tokenApprovals[_tokenId] = _approved;
        
    }
    
    function getApproved(uint256 _tokenId) public view returns (address) {
     return tokenApprovals[_tokenId];
    }
    
    
    function setApprovalForAll(address _operator, bool _approved) public {
        require(_operator != msg.sender); //권한 갖는 operator는 현재 메세지센더이면 안됨 (자가부여 X)
        operatorApprovals[msg.sender][_operator] = _approved; //_approved가 true - 허락, false면 거부
        
    }
    
    function isApprovedForAll(address _owner, address _operator) public view returns (bool) {
        return operatorApprovals[_owner][_operator];
        //setApprovalForAll의 operatorApprovals[][]값을 확인해서 해당값의 true/false 여부를 확인
        // 
    }
    function supportsInterface(bytes4 interfaceID) public view returns (bool) {
        return supportedInterfaces[interfaceID];
    }
    
    
    
    function isContract(address _addr) private view returns (bool) {
        uint256 size;
        assembly { size:= extcodesize(_addr) } //extcodesize의 주소를 넘겨서, 리턴한 값이 0이면 일반 계정.
        //0보다 크면 contract 계정
        return size > 0; //
    }
}
//토큰 경매시 중개인 필요
//이를 위한 외부 컨트랙트
contract Auction is ERC721TokenReceiver {
    function onERC721Received(address _operator, address _from, uint256 _tokenId, bytes _data) public returns(bytes4) {
        return bytes4(keccak256("onERC721Received(address,address,uint256,bytes)"));
          //이 리턴값이 위 magic value인 0x150b7a02가 됨
         
          
    }
    
    function checkSupportsInterface(address _to, bytes4 interfaceID) public view returns (bool){
        return ERC721Implementation(_to).supportsInterface(interfaceID);
    }
}

//각 인터페이스 표준들은 식별자로 구분되어있음.







