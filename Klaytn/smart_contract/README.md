
ERC165 
- 어떤 인터페이스ID를 넘기면 bool 반환.
- 

Magic value. 각 ERC 시리즈마다 식별자가 hash기반으로 있는데, 중요한것은 이 식별자값은 ERC 인터페이스내 함수에 의존적임.
함수가 바뀌게되면 식별자 값도 바뀜.
함수끼리 xor하고 hash구해 4bytes 로 짜름.

