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
import java.io.FileInputStream;
import java.io.IOException;
import java.net.URL;
import java.util.List;
import java.util.Properties;

import org.apache.commons.cli.CommandLine;
import org.apache.commons.cli.CommandLineParser;
import org.apache.commons.cli.HelpFormatter;
import org.apache.commons.cli.Option;
import org.apache.commons.cli.Options;
import org.apache.commons.cli.ParseException;
import org.apache.commons.cli.PosixParser;

import com.google.gdata.client.blogger.BloggerService;
import com.google.gdata.data.Category;
import com.google.gdata.data.Entry;
import com.google.gdata.data.Feed;
import com.google.gdata.data.PlainTextConstruct;
import com.google.gdata.util.AuthenticationException;
import com.google.gdata.util.ServiceException;

/**
 * TODO frogstarb -rename "old name.md" "new name.md"
 * 
 * @author Jonhnny Weslley - jw@jonhnnyweslley.net
 */
public class FrogstarB {

	public static final String VERSION = "0.1.0";

	private static final String FROGSTARB_PREFERENCES_FILE = ".frogstarb";
	private static final String METAFEED_URL = "http://www.blogger.com/feeds/default/blogs";
	private static final String FEED_URI_BASE = "http://www.blogger.com/feeds";
	private static final String POSTS_FEED_URI_SUFFIX = "/posts/default";
	private static final String BLOGGER_ATOM_NS = "http://www.blogger.com/atom/ns#";

	private final String feedUri;
	private final BloggerService blogger;

	public FrogstarB(String username, String password, String suggestedBlogId) throws Exception {
		blogger = new BloggerService("FrogstarB");
		blogger.setUserCredentials(username, password);

		String blogId = getBlogId(suggestedBlogId);
		feedUri = FEED_URI_BASE+"/"+blogId;
	}

	private String getBlogId(String suggestedBlogId) throws Exception {
		final URL feedUrl = new URL(METAFEED_URL);
		Feed resultFeed = blogger.getFeed(feedUrl, Feed.class);

		List<Entry> blogs = resultFeed.getEntries();
		if (blogs.size() == 0) {
			throw new IllegalStateException("Ooops! You don't have a blog yet!");

		} else if (blogs.size() == 1) {
			Entry blog = blogs.get(0);
			return blog.getId().split("blog-")[1];

		} else {
			if (suggestedBlogId != null) {
				for (Entry blog : blogs) {
					if (blog.getId().split("blog-")[1].equals(suggestedBlogId)) {
						return suggestedBlogId;
					}
				}

				boolean response = Console.confirm(true,
					"The blog with id '%s' doesn't exists. Select another blog and continue (Y/n)? ", suggestedBlogId);
				if (!response) {
					System.exit(5);
				}
			}

			System.out.println("List of your blogs:");
			for (int i = 1; i <= blogs.size(); i++) {
				Entry entry = blogs.get(i-1);
				System.out.println(i+" : "+entry.getTitle().getPlainText());
			}

			int selectedBlog = 0;
			try {
				selectedBlog = Console.readInt(Integer.MAX_VALUE, "Select one of them typing the blog number (Just press ENTER to exit): ");

			} catch (NumberFormatException e) {
				printAndExit("Invalid blog number.", null, 6);
			}

			if (selectedBlog == Integer.MAX_VALUE) {
				printAndExit("Bye!", null, 7);
			}

			require(selectedBlog > 0 && selectedBlog <= blogs.size(), "Selected blog number is out of range: [1,"+blogs.size()+"]");
			String blogId = blogs.get(selectedBlog - 1).getId().split("blog-")[1];
			System.out.println("The selected blog has id "+blogId);
			return blogId;
		}
	}

	public void publish(File file, String... tags) throws ServiceException, IOException {
		String postTitle = getPostTitle(file);
		Entry post = getPostByTitle(postTitle);

		if (post == null) {
			post = new Entry();
			configurePost(post, file, tags);
			URL postUrl = new URL(feedUri+POSTS_FEED_URI_SUFFIX);
			Entry insert = blogger.insert(postUrl, post);
			System.out.println("Your blog post was published successfully! I'm so happy! :D");
			System.out.println("View post at "+insert.getHtmlLink().getHref());

		} else {
			configurePost(post, file, tags);
			URL editUrl = new URL(post.getEditLink().getHref());
			Entry update = blogger.update(editUrl, post);
			System.out.println("Your blog post was updated successfully! I'm so happy! :D");
			System.out.println("View post at "+update.getHtmlLink().getHref());
		}
	}

	public void delete(File file) throws ServiceException, IOException {
		String postTitle = getPostTitle(file);
		Entry post = getPostByTitle(postTitle);
		if (post == null) {
			printAndExit("Post not found: \""+postTitle+"\"", null, 8);

		} else {
			URL deleteUrl = new URL(post.getEditLink().getHref());
			blogger.delete(deleteUrl);
			System.out.println("Your blog post was deleted!");
		}
	}

	private void configurePost(Entry post, File file, String... tags) throws IOException {
		String postTitle = getPostTitle(file);
		MarkupLanguage markupLanguage = getMarkupLanguage(file);
		String content = markupLanguage.translate(file);
		post.setTitle(new PlainTextConstruct(postTitle));
		post.setContent(new PlainTextConstruct(content));
		for (String tag : tags) {
			if (tag.startsWith("-")) {
				post.getCategories().remove(new Category(BLOGGER_ATOM_NS, tag.substring(1)));
			} else {
				post.getCategories().add(new Category(BLOGGER_ATOM_NS, tag));
			}
		}
	}

	private Entry getPostByTitle(String title) throws IOException, ServiceException {
		URL feedUrl = new URL(feedUri+POSTS_FEED_URI_SUFFIX);
		Feed resultFeed = blogger.getFeed(feedUrl, Feed.class);

		for (Entry entry : resultFeed.getEntries()) {
			if (entry.getTitle().getPlainText().equals(title)) {
				return entry;
			}
		}
		return null;
	}

	private String getPostTitle(File file) {
		String filename = file.getName();
		int dot = filename.lastIndexOf('.');
		return (dot == -1) ? filename : filename.substring(0, dot);
	}

	private MarkupLanguage getMarkupLanguage(File file) {
		String filename = file.getName();
		int dot = filename.lastIndexOf('.');
		if (dot == -1) {
			System.out.println("WARN: This file has not an extension. I will upload the file content as plain text.");
			return MarkupLanguage.PlainText;
		}

		String markupExtension = filename.substring(dot+1);
		MarkupLanguage markupLanguage = MarkupLanguage.byFileExtension.get(markupExtension);
		if (markupLanguage == null) {
			System.out.println("WARN: This file extension '"+markupExtension+
			"' has not a markup parser. I will upload the file content as plain text.");
		}
		return markupLanguage == null ? MarkupLanguage.PlainText : markupLanguage;
	}

	private static File toFile(String filename) {
		File file = new File(filename);
		require(file.exists(), "File not found: "+file);
		require(file.isFile(), "File is a directory: "+file);
		require(file.canRead(), "No permission to read the file: "+file);
		return file;
	}

	private static void require(boolean value, String message) {
		if (!value) {
			throw new IllegalArgumentException(message);
		}
	}
	
	private static void printAndExit(String msg, Exception cause, int exitCode) {
		System.err.println(msg);
		if (cause != null) {
			System.out.println("DETAILS:");
			cause.printStackTrace(System.err);
		}
		System.exit(exitCode);
	}

	private static Properties getUserPreferences() {
		Properties properties = new Properties();
		try {
			properties.load(new FileInputStream(new File(System.getProperty("user.home"), FROGSTARB_PREFERENCES_FILE)));
		} catch (IOException e) {
			// ignore
		}
		return properties;
	}

	public static void addOption(Options options, String opt, String longOpt, String argName, String description) {
		Option option = new Option(opt, longOpt, true, description);
		option.setArgName(argName);
		options.addOption(option);
    }

	public static void main(String[] args) throws Exception {
		Options options = new Options();
		addOption(options, "e", "email", "EMAIL",
			"The email of the blogger user. This option is not required if " +
			"the 'email' property is defined in the configuration file '~/.frogstarb'.");
		addOption(options, "P", "password", "PASSWORD",
			"The password of the blogger user. This option is not required if " +
			"the 'password' property is defined in the configuration file '~/.frogstarb'.");
		addOption(options, "b", "blog-id", "BLOGID",
			"The blog's id. This option is not required if either the blogger user has just one blog " +
			"or the 'blog-id' property is defined in the configuration file '~/.frogstarb'.");
		addOption(options, "t", "tags", "TAG_LIST",
			"The list of tags to be added or removed from the post, specified as a comma-separated list. " +
			"If the tag name starts with '-' then it will be removed, otherwise it will be added to the post's list of tags.");
		addOption(options, "p", "publish", "FILENAME",
			"Publish the post. If the post doesn't exist yet, it will be created; otherwise the post will be updated.");
		addOption(options, "d", "delete", "FILENAME",
			"Delete the post.");
		options.addOption("v", "version", false,
			"Display current version and exit.");
		options.addOption("h", "help", false,
			"Display this help and exit.");

		try {
			CommandLineParser parser = new PosixParser();
			CommandLine line = parser.parse(options, args);

			if (line.hasOption("version")) {
				System.out.printf("frogstarb %s", VERSION);
				System.exit(0);
			}

			if (line.hasOption("help")) {
				HelpFormatter formatter = new HelpFormatter();
				formatter.printHelp(80,"frogstarb [OPTIONS] ... [-p <FILENAME>] [-d <FILENAME>]",
				"\nfrogstarb creates, updates and deletes posts on blogger.com\nOptions:\n\n", options, "");
				System.exit(0);
			}

			Properties properties = getUserPreferences();
			String email = line.hasOption("email") ? line.getOptionValue("email") : properties.getProperty("email");
			String password = line.hasOption("password") ? line.getOptionValue("password") : properties.getProperty("password");
			String blogId = line.hasOption("blog-id") ? line.getOptionValue("blog-id") : properties.getProperty("blog-id");

			if (password == null || password.trim().isEmpty()) {
	            password = Console.readString("Enter your password(%s): ", email);
			}

			if (line.hasOption("publish")) {
				String[] tags = line.hasOption("tags") ? line.getOptionValue("tags").trim().split(",") : new String[0];
				File postFile = toFile(line.getOptionValue("publish"));

				System.out.println("file: "+postFile);
				System.out.println("file: "+postFile.getAbsolutePath());
				(new FrogstarB(email, password, blogId)).publish(postFile, tags);

			} else if (line.hasOption("delete")) {
				File postFile = toFile(line.getOptionValue("delete"));
				(new FrogstarB(email, password, blogId)).delete(postFile);

			} else {
				System.out.println("No actions to be taken! :P");
			}

		} catch (IllegalArgumentException e) {
			printAndExit(e.getMessage(), null, 1);
		} catch (IllegalStateException e) {
			printAndExit(e.getMessage(), null, 2);
		} catch (ParseException e) {
			printAndExit(e.getMessage(), null, 3);
		} catch (AuthenticationException e) {
			printAndExit("Authentication failed! Please, check your credentials.", e, 4);
		}
	}

}
