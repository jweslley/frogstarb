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
package frogstarb;

import java.io.File;
import java.io.FileReader;
import java.io.IOException;
import java.io.StringWriter;
import java.util.HashMap;
import java.util.Map;

import net.java.textilej.parser.MarkupParser;
import net.java.textilej.parser.builder.HtmlDocumentBuilder;
import net.java.textilej.parser.markup.textile.TextileDialect;

import com.petebevin.markdown.MarkdownProcessor;

public abstract class MarkupLanguage {

	public final String name;

	public MarkupLanguage(String name) {
		this.name = name;
	}

	public abstract String translate(String source);

	public final String translate(File file) throws IOException {
		StringWriter writer = new StringWriter();
		FileReader reader = new FileReader(file);
		try {
			int c;
			while ((c = reader.read()) != -1) {
				writer.write(c);
			}
		} finally {
			reader.close();
		}
		return translate(writer.toString());
	}

	/**
	 * <code>
	 * h1. Congratulations!
	 *
	 * You read a *textile* document.
	 * </code>
	 */
	public static final MarkupLanguage Textile = new MarkupLanguage("textile") {

		@Override
		public String translate(String source) {
			StringWriter out = new StringWriter();
			MarkupParser parser = new MarkupParser(new TextileDialect(), new HtmlDocumentBuilder(out));
			parser.parse(source, false);
			return out.toString();
		}

	};

	/**
	 * <code>
	 * # Congratulations!
	 *
	 * You read a *markdown* document.
	 * </code>
	 */
	public static final MarkupLanguage Markdown = new MarkupLanguage("markdown") {

		@Override
		public String translate(String source) {
			MarkdownProcessor markdown = new MarkdownProcessor();
			return markdown.markdown(source);
		}

	};

	/**
	 *
	 */
	public static final MarkupLanguage PlainText = new MarkupLanguage("text") {

		@Override
		public String translate(String source) {
			return source;
		}

	};

	public static final Map<String, MarkupLanguage> byFileExtension = new HashMap<String, MarkupLanguage>() {{
		put("textile", Textile);
		put("md", Markdown);
		put("txt", PlainText);
	}};

}
