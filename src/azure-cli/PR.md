**Description**

This PR addresses #24542 by updating the current dependency on the JMESPath language used in the `--query` command-line argument.

**Testing Guide**

az CLI uses the JMESPath language to power its `--query` command-line argument.
For instance, consider the following current behaviour:

- `` az storage account list --query "[].{location: location, name:name}" ``: 

```json
[
  { "location": "westeurope", "name": "storageaccount-001" },
  { "location": "westeurope", "name": "storageaccount-002" },
  { "location": "northeurope", "name": "storageaccount-003" },
  { "location": "westus", "name": "storageaccount-004" },
  { "location": "westus", "name": "storageaccount-005" }
]
```

Here is a new query that can be performed using JMESPath Community:

```sh
az storage account list \
  --query "group_by([].{loc: location, n:name}, &loc).*.let( {key: [0].loc, values: [*].n}, &{key: key, values: values})|from_items(zip([*].key, [*].values))"
``` 

with the corresponding result:

```json
{
  "westeurope": [ "storageaccount-001", "storageaccount-002" ],
  "northeurope": [ "storageaccount-003" ],
  "westus": [ "storageaccount-004", "storageaccount-005" ]
}
```

While there is definitely a learning curve to JMESPath, this example features most of the improvements we’ve made to the specification.

The full expression can be broken down into chunks:

- `` group_by([].{loc: location, n: name}, &loc) ``: creates a new hash with the subset of interesting `location` and `names` properties from the original object. It uses the new `group_by()` function to split the result by location.
- `` .* ``: is a value projection to create an array that can be iterated upon subsequently.
- `` let( {key: [0].loc, values: [*].n}, &{key:key, values:values}) ``: expression that is evaluated for each item in the projected array. It uses the new `let()` function to take advantage of lexical scoping.
  - Its first argument initialize a new scope with the two `key` and `values` properties that contain the value of the `loc` property from the first array entry – as all entries contain the same location at this stage – and the list of names respectively.
  - Its second argument creates a hash with the two aforementioned properties.
- `` | ``: the pipe stops the projection so that later expressions operate on the full array instead of being evaluated iteratively on each array element.
- `` from_items(zip([*].key, [*].values)) ``: creates the expected result.
  - It uses the new `zip()` function to combine the list of `key` elements and the `values` arrays into a single entity.
  - It then uses the new `from_items()` functions to combine those two lists like for like to produce the resulting object shown above.

**Overview**

This PR is a draft as I would like to make the most effort to help include an updated JMESPath language with an improved feature set to az CLI. However, I’m not sure what would be the reasonable changes to do or if it should be broken into multiple pull requests. I would also likely need guidance over how to best fill the PR description template.

This PR makes the following changes:

- Replaces all mentions of the `jmespath.org` original web site to the new `jmespath.site`.
- Replaces original dependencies over `jmespath` Python package to the new `jmespath-community` Python package.
- Replaces original dependencies over `jmespath-terminal` (`jpterm` helper) Python CLI tool to the new `jmespath-community-terminal` tool in Docker images.
- Replaces original `github.com/jmespath/jp` CLI tool by the new `github.com/jmespath-community/jp` CLI tool in Docker images.
- Updates minimum Python version to `3.7.16` for some Docker image.
- Updates various documentation pages while keeping the same LICENSE requirements.

I’m not sure if all the documentation pages must be updated though.

**JMESPath Community**

This PR aims to include [JMESPath Community](https://jmespath.site/main/) assets into az CLI.

JMESPath Community is a new initiative to bring improvements to and steward the specification going forward,
as the language and its tools no longer appear to be maintained. As its first milestone,
JMESPath Community includes the following improvements to the original specification:

- JEP-11 Lexical Scoping
- JEP-12a Raw String Literals
- JEP-13 Object Manipulation functions
- JEP-14 String functions
- JEP-15 String Slices
- JEP-16 Arithmetic Expressions
- JEP-17 Root Reference
- JEP-18 Grouping
- JEP-19 Standardized Evaluation of Pipe Expressions

JMESPath Community also aims to be an umbrella for specific programming language implementations. It currently hosts the following 100% compliant implementations:

- [jmespath-community (Python)](https://pypi.org/project/jmespath-community/)
- [jmespath-community-terminal (Python)](https://pypi.org/project/jmespath-community-terminal/)
- [go-jmespath (Golang)](https://pkg.go.dev/github.com/jmespath-community/go-jmespath)
- [jp (Golang)](https://github.com/jmespath-community/jp)

I’m also the co-author of the [JMESPath.Net](https://jdevillard.github.io/JmesPath.Net/) implementation 🤐.

For the purpose of az CLI, JMESPath Community is a drop-in replacement for the original `jmespath` Python package. It maintains backwards compatibility with the original language to prevent breaking existing syntax and scripts.

The various built-in Docker images re-introduce `jpterm` which has seen its dependencies updated and [no longer breaks the CI](https://github.com/Azure/azure-cli/pull/21206).

The accompanying `jp` executable has also been brought up to standards and is included in this PR.