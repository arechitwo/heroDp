
## 파일 타입 안내

- 이 프로젝트의 .eps 파일은 EPScript(EUD Editor 스크립트) 텍스트 코드이며, PostScript 이미지가 아니다.
- .eps 파일은 항상 일반 텍스트로 취급하고 Read/Edit 도구를 정상적으로 사용한다.
- Read 도구가 바이너리로 오인하더라도, `cat` 이나 텍스트 모드로 강제 읽어서 Edit(str_replace)로 부분 수정할 것. Python 스크립트로 전체 재작성하지 말 것.
