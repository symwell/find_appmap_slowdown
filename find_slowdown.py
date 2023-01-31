import subprocess

def exec_cmd(command):
    p = subprocess.Popen(
        command,
        shell=True,
        stdout=subprocess.PIPE,
        stdin=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    output, _ = p.communicate()
    return output.decode()

def rspec_runtime_str_to_secs(runtime_str):
    if runtime_str.find("minute") != -1 or runtime_str.find("minutes") != -1:
        values = runtime_str.split(" ")
        return float(values[0]) * 60 + float(values[2])
    else:
        # only seconds
        values = runtime_str.split("seconds")
        return float(values[0])


files_str = exec_cmd("find spec/requests | grep .rb | xargs echo -n")
files = files_str.split()

exec_cmd("mkdir -p profile_results")

start_from = 'spec/requests/stories/tagged_articles_spec.rb'
#start_from = None

file_times = {}
for file in files:
    if start_from and file != start_from:
        continue
    else:
        start_from = None
    file_no_slashes = file.replace("/", "___")
    print(file, flush=True)
    file_times[file] = {
    }
    for mode in ["false", "true"]:
        padding = ' '
        if mode == 'true':
            padding = '  '
        print("  APPMAP=" + mode + padding, end='', flush=True)
        exec_cmd("APPMAP=" + mode +" RAILS_ENV=test bundle exec rspec " + file + " > profile_results/test_" + mode + "___" + file_no_slashes)
        runtime_str = exec_cmd("cat profile_results/test_" + mode + "___" + file_no_slashes + " | grep 'Finished in' | sed -e 's/.*Finished in //g' | sed -e 's/(.*//g' | xargs echo -n")
        runtime = rspec_runtime_str_to_secs(runtime_str)
        file_times[file][mode] = { "runtime": runtime }        
        print(runtime, flush=True)

    factor = file_times[file]["true"]["runtime"] / file_times[file]["false"]["runtime"]
    factor = round(factor, 2)
    print("               " + str(factor) + "x ", end='', flush=True)
    if factor > 2:
        print("MUCH SLOWER *** *** *** *** ***", flush=True)
    elif factor > 1:
        print("slower", flush=True)
    elif factor < 1:
        print("faster", flush=True)
    elif factor == 1:
        print("same", flush=True)