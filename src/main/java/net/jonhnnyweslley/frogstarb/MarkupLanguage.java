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

import java.io.File;
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

	public final String translate(File file) throws Exception {
		String code = Code.codify(file);
		return translate(code);
	}

	/**
	 * <code>
	 * h1. Congratulations!
	 * <br/><br/>
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
	 * <br/><br/>
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
	 * <code>
	 * &lt;h1&gt;Congratulations!&lt;/h1&gt;
	 * <br/><br/>
	 * &lt;p&gt;You read a &lt;b&gt;html&lt;/b&gt; document.&lt;/p&gt;
	 * <code>
	 */
	public static final MarkupLanguage PlainText = new MarkupLanguage("text") {

		@Override
		public String translate(String source) {
			return source;
		}

	};

	public static final Map<String, MarkupLanguage> byFileExtension = new HashMap<String, MarkupLanguage>() {{
		put("txt", PlainText);
		put("textile", Textile);
		put("markdown", Markdown);
		put("mkdn", Markdown);
		put("mkd", Markdown);
		put("md", Markdown);
	}};

}
