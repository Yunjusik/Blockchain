pragma solidity ^0.4.24;

contract MyName {
    string myName = "Jusik";

    function getMyName() constant public returns(string) {
        return myName;
    }
}
