import sbt._

class FrogstarBProject(info: ProjectInfo) extends DefaultProject(info) {

  val java_net = "Java.net repo" at "http://download.java.net/maven/2"
  val mandubian = "mandubian" at "http://mandubian-mvn.googlecode.com/svn/trunk/mandubian-mvn/repository/"

  val core = "com.google.gdata" % "gdata-core-1.0" % "1.41.1"
  val media = "com.google.gdata" % "gdata-media-1.0" % "1.41.1"
  val client = "com.google.gdata" % "gdata-client-1.0" % "1.41.1"
  val client_meta = "com.google.gdata" % "gdata-client-meta-1.0" % "1.41.1"
  val blogger = "com.google.gdata" % "gdata-blogger-2.0" % "1.41.1"
  val blogger_meta = "com.google.gdata" % "gdata-blogger-meta-2.0" % "1.41.1"
  val gcollect = "com.google.collections" % "google-collections" % "1.0-rc1"

  val cli = "commons-cli" % "commons-cli" % "1.2"

  val velocity = "org.apache.velocity" % "velocity" % "1.6.4"
  val markdown = "org.markdownj" % "markdownj" % "0.3.0-1.0.2b4"
  val textile = "net.java" % "textile-j" % "2.2"

  val specs = "org.scala-tools.testing" % "specs" % "1.6.1" % "test"
  val mockito = "org.mockito" % "mockito-all" % "1.8.1" % "test"

}
