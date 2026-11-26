#!/bin/bash
# 빠른 컴파일(메이븐을 띄우지 않고 javac 로) — 개발 · 정답지 대조용. 정식 묶음은 mvn package
cd "$(dirname "$0")"
CP=$(find ~/.m2/repository/org/apache/pdfbox ~/.m2/repository/com/microsoft/playwright ~/.m2/repository/commons-logging ~/.m2/repository/com/google/code/gson -name "*.jar" 2>/dev/null | grep -v -e sources -e javadoc | tr '\n' ':')
mkdir -p target/classes target/test-classes
javac -nowarn -encoding UTF-8 --release 17 -cp "$CP" -d target/classes $(find src/main/java -name "*.java") 2>&1 | grep -v "^Picked up\|^Note:" 
T=$(find src/test/java -name "*.java" 2>/dev/null)
[ -n "$T" ] && javac -nowarn -encoding UTF-8 --release 17 -cp "target/classes:$CP" -d target/test-classes $T 2>&1 | grep -v "^Picked up\|^Note:"
echo "$CP" > target/cp.txt
