# Better Option -database

Database of better options for various things with issues.

# Contributing

There are two main ways to contribute to the database, if you want to simply add more content.

1. Pull request - make changes to `problems`, `things`, `problems/classes`, or `things/categories` with your proposed changes. Don't feel overwhelmed, Markdown and YAML are easy to write even for non-techies.
2. Create an [issue](https://github.com/lietu/BetterOption/issues/new) with enough information. Please check the [issue list](https://github.com/lietu/BetterOption/issues) first though to ensure it's not a known issue.

For new content it is a good idea to add information on what the problems exactly are, why they are important, and any references to source material that can be used to verify the claims.

Additionally you can of course contribute to the site's layout and structure, or other scripts. Similarly you can make a direct Pull Request, or submit an issue with the necessary details.

## Adding content

The content is spread to multiple folders, formatted in [Markdown](https://daringfireball.net/projects/markdown/syntax) with [YAML front matter](https://jekyllrb.com/docs/front-matter/) for data.

Basically every file looks like this:

```markdown
---
item_name: Environmental
image: water-pollution
---
Environmental concerns contribute to pollution, global warming, and such issues, or e.g. can negatively affect marine life.
```

The section between the two sets of `---`s is the "front matter", basically configuration for how it will be understood by the system, and this is different for each item type.

The bit after the front matter (below the second `---`) is then the content for that entry, in Markdown format.

The folders are:

 - [images/](images/) - Contains both image files and the necessary data to go with them
 - [problems/](problems/) - The various different types of problems, e.g. Microplastics
 - [problems/classes/](problems/classes/) - The problem classification, e.g. Environmental
 - [things/](things/) - The various things, e.g. Polyester or Cotton
 - [things/categories/](things/categories/) - The categories for things, e.g. Clothes

### Common things

In the YAML front matter there are a few fields that are common among all the different types of files except `images`.

```yaml
item_name: Environmental
```

This sets the name of the thing when displayed on the site. When referring to it from other files you should use the filename without the extension though, and it is case sensitive.

E.g. if `problems/classes/environmental.md` says `item_name: Environmental`, then to make a problem belong to that class you should use `class: environmental` (notice lowercase name as in the filename) in the file under `problems/`.

```yaml
image: microplastics
```

This sets the image to use for the item. Again it refers to the filename pointing to the `.md` file, so e.g. `image: microplastics` means there needs to be a file called `images/microplastics.md` with more data about the image in it.

For more complete examples check the folders in question, but below are some details and explanations about the formatting.

### Images

Do not add copyrighted content or content that is not easily traceable to its source with a clear license. This to ensure there is no liability concerns in the future.

You should also try to keep the image sizes reasonable, it's unlikely we'll need >1024x1024 resolution images of anything, so if it's big - please scale it down before adding it.

Examples of suitable licenses are:

 - Public Domain
 - Creative Commons Zero (CC-0)
 - Creative Commons Attribution, incl. Share-Alike, NonCommercial-ShareAlike

The image files need to define the following properties in the YAML front matter:

 - `source`: Where this image is from - e.g. link to Wikimedia Commons if that's where you got it from
 - `filename`: The actual filename of the image file in the `images/` folder that should be used. E.g. `cotton.jpg`. Case-sensitive.
 - `license`: The license the image is distributed with.
 - `attribution_url`: (if available or required by license) Link to the person who made the image
 - `author`: (if available or required by license) Name or username of the person who made the image

### Problems

In addition to the previously mentioned `image_name` and `image` the fields for problems are:

 - `class`: The name of the *problem class* the problem belongs to. Based on the filename, not the `item_name`. E.g. `environmental`. Case-sensitive.
 - `sources`: List of URLs to reference material, i.e. what are the sources of the claims made about this problem. Wikipedia is ok, but other sources, especially high grade peer-reviewed scientific papers, would be preferred.

### Problem classes

There is nothing special about the definitions for problem classes. Add the `item_name` and `image` to the YAML front matter and a description in the Markdown content.

### Things

In addition to the previously mentioned `image_name` and `image` the fields for things are:

 - `category`: The name of the *category of things* the thing belongs in. Based on filename, not the `item_name`. E.g. `clothes`. Case-sensitive.
 - `problems`: List of *problems* with the thing. Based on filename, not the `item_name`. Case-sensitive.
 - `options`: List of `raw_name` + `description` for the options for the thing, if any.
 - `options.raw_name`: The name of the *thing* that is a viable alternative to this one. Based on the filename, not the `item_name`. E.g. `cotton`. Case-sensitive.
 - `options.description`: A short description as to why this option is worth considering.
 - `sources`: List of URLs to reference material, i.e. what are the sources of the claims made about the problems with the thing. Wikipedia is ok, but other sources, especially high grade peer-reviewed scientific papers, would be preferred.

### Categories of things

There is nothing special about the definitions for categories either. Add the `item_name` and `image` to the YAML front matter and a description in the Markdown content.

# License

All contents of this repository are, unless otherwise specified, under
the 3-clause BSD license. Details in [LICENSE.md](LICENSE.md).
