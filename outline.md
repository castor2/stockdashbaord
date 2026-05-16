
-- Overview
매크로 경제지표에 대해 한눈에 볼 수 있는 대시보드 구성

-- Implementation
데이터는 유튜브 영상 
https://www.youtube.com/watch?v=35B8iC2KD8U&list=PLIk4JNQzz-mTDPDdKQ7St2mM-0GC7w82Q
에 나오는 버블지표 7개와 반론지표 5개로 구성 

각 지표는 시계열 그래프라 대시보드의 구현은 grafana를 이용하면 좋겠고, 한 대시보드에 12개의 패널이 보이게 하면 좋겠어. 
그리고 다른 플랫폼에 쉽게 이식되도록 docker 기반으로 구성해줘

-- 데이터 확보
데이터를 어떻게 확보할지에 대해서도 찾아봐주고, 최근 3년간의 데이터를 구해봐줘. 

-- test
구현하고 나서는 로컬 브라우저를 띄워서 실제 잘 구성되었는지 확인해줘. 


-- source management 
오늘 진행된 작업은 github에 유튜브 소스, 지표리스트, 다른 시스템에 포팅방법까지 포함하여 README.md 작성하고,  
github 에 push 해줘 

