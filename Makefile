VERSION=0.1.0

download-dependencies:
	if [ ! -d "lib" ] ; then mkdir lib;	fi
	wget http://gdata-java-client.googlecode.com/files/gdata-src.java-1.41.2.zip
	wget http://download.java.net/maven/2/net/java/textile-j/2.2/textile-j-2.2.jar
	wget http://markdownj.googlecode.com/files/markdownj-1.0.2b4-0.3.0.jar
	wget http://linorg.usp.br/apache/commons/cli/binaries/commons-cli-1.2-bin.zip
	unzip gdata-src.java-1.41.2.zip > /dev/null
	unzip commons-cli-1.2-bin.zip > /dev/null
	cp gdata/java/deps/google-collect-1.0-rc1.jar lib/
	cp gdata/java/lib/gdata-blogger-* lib/
	cp gdata/java/lib/gdata-client-* lib/
	cp gdata/java/lib/gdata-core-1.0.jar lib/
	cp gdata/java/lib/gdata-media-1.0.jar lib/
	cp commons-cli-1.2/commons-cli-1.2.jar lib/
	rm -rf gdata* commons-cli*
	mv *.jar lib/

compile:
	if [ ! -d "classes" ] ; then mkdir classes; fi
	javac -cp "classes/:lib/*" -d classes/ src/**/**

create-jar: compile
	jar cvf lib/frogstarb-$(VERSION).jar -C classes/ classes/frogstarb/*

package: create-jar
	zip -r frogstarb-$(VERSION).zip bin lib LICENSE.txt README.md
