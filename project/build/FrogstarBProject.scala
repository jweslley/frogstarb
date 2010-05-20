import sbt._

class FrogstarBProject(info: ProjectInfo) extends DefaultProject(info) {

  val java_net = "Java.net repo" at "http://download.java.net/maven/2"

  val cli = "commons-cli" % "commons-cli" % "1.2"

  val velocity = "org.apache.velocity" % "velocity" % "1.6.4"
  val markdown = "org.markdownj" % "markdownj" % "0.3.0-1.0.2b4"
  val textile = "net.java" % "textile-j" % "2.2"

  val specs = "org.scala-tools.testing" % "specs" % "1.6.1" % "test"
  val mockito = "org.mockito" % "mockito-all" % "1.8.1" % "test"

}
