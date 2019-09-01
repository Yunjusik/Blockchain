//var HDWalletProvider = require("truffle-hdwallet-provider");
//var mnemonic = "giant dizzy dumb strike economy music gather steak pattern swear visit apple";
module.exports = {
     // See <http://truffleframework.com/docs/advanced/configuration>
     // to customize your Truffle configuration!
     networks: {
          ganache: {
               host: "localhost",
               port: 7545,
               network_id: "*" // Match any network id
          },
          //ropsten: {
            //   provider: function(){
             //       return new HDWalletProvider(mnemonic, 'https://ropsten.infura.io/v3/ae36b3186eaa40f8830b5007c4d4e3ca')
              // },
               //network_id: '3',
               //gas:4500000,
               //gasPrice: 10000000000,
          
          //}
     }
};
