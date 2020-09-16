# Changelog Generator (ClogG)

ClogG is a simple CLI for generating basic changelog files from git commits.

The generation of changelogs ist based on the commit history, including release tags. The commit history must follow the syntax described below to be effective.

## Commit Syntax

The script separates between four parts of a single commit following the Syntax:

```
[<type>] <title>

(<category>) <description>
```



**Example:**

```
[feat] Implemented a fancy new login page

(Login) A long and interesting description of the new login page
```

**compiles to:**

---

#### New Features

  - **Login:** Implemented a fancy new login page

    > A long and interesting description of the new login page

---

### Type

The commit types are based on (but not identical to) [Angular commit types](https://github.com/angular/angular.js/blob/master/DEVELOPERS.md#type) and written in square brackets. As the brackets are used to indicate that a commit should be added to the changelog, you can still use commit types without brackets for all of your commits and simply add brackets to those which should be included in the changelog file.

ClogG currently supports the following Types. They are not case sensitive:

| Type  | Meaning                                |
| ----- | -------------------------------------- |
| break | Breaking changes                       |
| build | Changes to build system / dependencies |
| docs  | Documentation changes                  |
| feat  | New features                           |
| fix   | Bugfixes                               |
| misc  | Miscellaneous                          |
| perf  | Performance improvements               |
| refac | Refactoring                            |
| test  | Tests                                  |

#### Adding your own Types

New types can be easily added by appending the tag (max. 5 characters) to the `Types` enum and adding a description to `TYPE_TEXT`

### Title

This is should be a short title for the committed changes to add to the Changelog

### Category

A category is added by placing it at the beginning of the commit description in parentheses. Categories are optional and can consist of any combination of Characters and Numbers (including whitespaces).

### Description

The description of a commit allows to give additional information for an implemented change. The description of a commit is optional and can also be used without a prepending category.

### Version

The resulting changelog is grouped by releases indicated by tags. The versioning must follow the [semantic versioning syntax](semver.org). A `v`  at the beginning is also allowed. At this point ClogG does not interpret the version numbers. The changelog is solely structured by the order of version tags from the commit history.

Examples:

- `v1.3.5`
- `6.3.2`
- `v6.3.21-rc.3`
- `V3.2.4-beta1`



