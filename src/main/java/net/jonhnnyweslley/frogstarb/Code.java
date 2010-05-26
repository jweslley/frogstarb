/**
 * Copyright (C) 2010 Jonhnny Weslley
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *         http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */
package net.jonhnnyweslley.frogstarb;

import java.io.BufferedReader;
import java.io.File;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.io.PrintWriter;
import java.io.Reader;
import java.io.StringWriter;
import java.io.Writer;
import java.util.Properties;

import org.apache.velocity.Template;
import org.apache.velocity.VelocityContext;
import org.apache.velocity.app.Velocity;
import org.apache.velocity.context.InternalContextAdapter;
import org.apache.velocity.exception.MethodInvocationException;
import org.apache.velocity.exception.ParseErrorException;
import org.apache.velocity.exception.ResourceNotFoundException;
import org.apache.velocity.runtime.directive.Directive;
import org.apache.velocity.runtime.parser.node.Node;

public class Code extends Directive {

	public static final boolean PYGMENTS = Boolean.getBoolean("pygments");
	public static final String PYGMENTIZE_BIN = System.getProperty("pygments.path", "pygmentize");
	public static final String FILE_ENCONDING = System.getProperty("file.encoding", "UTF-8");

	@Override
	public String getName() {
		return "code";
	}

	@Override
	public int getType() {
		return BLOCK;
	}

	@Override
	public boolean render(InternalContextAdapter context, Writer writer,
			Node node) throws IOException, ResourceNotFoundException,
			ParseErrorException, MethodInvocationException {

		if (node.jjtGetNumChildren() < 2) {
			// TODO better exception message
			System.out.println(node.getLine());
			System.out.println(node.getTemplateName());
            throw new IllegalArgumentException("no lang");
        }
		String lang = String.valueOf(node.jjtGetChild(0).value(context));

		StringWriter blockContent = new StringWriter();
		node.jjtGetChild(1).render(context, blockContent);
		String code = blockContent.toString();

		if (PYGMENTS) {
			writer.write(pygmentize(lang, code));
		} else {
			writer.write(code);
		}

		return true;
	}

	private String pygmentize(String lang, String code) {
		try {
			String[] args = new String[] { PYGMENTIZE_BIN, "-l", lang, "-f", "html", "-O", "encoding="+FILE_ENCONDING };
			Process p = Runtime.getRuntime().exec(args);

			InputStream stdOut = p.getInputStream();
			PrintWriter in = new PrintWriter(p.getOutputStream());
			in.write(code);
			in.close();

			int exitCode = p.waitFor();

			if (exitCode == 0) {
				return readAll(stdOut);
			}
			System.out.println("WARN"); // FIXME

		} catch (IOException e) {
			System.out.println("WARN: pygmentize program not found. Check if you have pygmentize installed on your system.");

		} catch (InterruptedException e) {
			System.out.println("WARN: pygmentize program not found. Check if you have pygmentize installed on your system.");
		}

		return code;
	}

	private String readAll(InputStream source) throws IOException {
		StringWriter writer = new StringWriter();
		Reader reader = new BufferedReader(new InputStreamReader(source));
		try {
			int c;
			while ((c = reader.read()) != -1) {
				writer.write(c);
			}

		} finally {
			reader.close();
		}

		return writer.toString();
	}

	public static String codify(File file) throws Exception {
		Properties properties = new Properties();
		properties.put("userdirective", Code.class.getName());

		Velocity.init(properties);
		Template template = Velocity.getTemplate(file.toString(), FILE_ENCONDING);

		StringWriter code = new StringWriter();
		template.merge(new VelocityContext(), code);
		return code.toString();
	}

}