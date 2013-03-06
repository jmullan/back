back
====

A script to assist with backing up individual files and directories.

Usage: back [options] file1 dir1 file2

Options:
  -h, --help show this help message and exit
  -f FROM_ROOT, --from=FROM_ROOT Use this as the source root
  -t TO_ROOT, --to=TO_ROOT Use this as the backup root
  --push Look in the sources for root of file
  --pull Look in the destinations for root of file

Perhaps this is best explained by example.

With three directories:
/tmp/foo
/tmp/bar
/tmp/baz

Where /tmp/foo has some directories and files in it:
/tmp/foo/monkey
/tmp/foo/pirate
/tmp/foo/ninja/samurai

You might want to rsync from /tmp/foo to /tmp/bar

rsync /tmp/foo /tmp/bar

That would make /tmp/bar/foo. I make this mistake all the time.

So, create a file ~/.back.ini with the contents
[/tmp/foo]
dest=/tmp/bar

Running this command:
back /tmp/foo/

would cause back to look up /tmp/foo in the ini, see that it is a source root, and correctly rsyncs it. Obviously, that is a trivial case, but a more interesting case is when you are recovering files from a failing drive or migrating from one directory to another -- you can set up your source and destination, change into the source, and copy over just the files you want.

cd /tmp/foo
back monkey
back ninja/samurai
