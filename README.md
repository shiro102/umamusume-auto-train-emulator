# Umamusume Auto Train Phone Emulator

This is a fork from [samsulpanjul/umamusume-auto-train](https://github.com/samsulpanjul/umamusume-auto-train)

If you ever get tired during or after a bad run and don't want to keep training, or if you just want to farm sparks lazily, this is the solution for you. This is a simple auto-training for Umamusume.

This project is inspired by [shiokaze/UmamusumeAutoTrainer](https://github.com/shiokaze/UmamusumeAutoTrainer)

[Demo video](https://youtu.be/CXSYVD-iMJk)

### DISCLAIMER: There are bugs sometimes because app uses OCR screen reading for options, so please DO NOT use this tool to train your ace. However thanks to that there is ALMOST ZERO chance of getting banned by Cygames. I have used it since the launch of the game. But still don't reveal your ID with the app (in the same image, ... ).

### THÔNG BÁO: App này sẽ đôi khi có lỗi vì nó chụp màn hình để chọn option, nên ĐỪNG DÙNG nó để train ngựa ace. Nhưng nhờ thế nên là sẽ GẦN NHƯ KHÔNG CÓ KHẢ NĂNG BỊ BAN bởi Cygames. Mình đã dùng nó từ khi game mở tới giờ. Nhưng mà bạn cũng ko nên lộ ID lúc dùng app như là chụp ảnh đăng lên group, ...

# Language
1. [English](#english)
2. [Tiếng Việt](#tiếng-việt)

# UPDATE:
- Support Aoharu Scenario
- Support Riko Kashimoto date

Get new updates using "git pull" in Command Prompt or PowerShell at the tool's folder location

## English
### Features
- Auto choose option with energy (2nd year, 3rd year, new year, extra training). Hard-code some events of Kitasan Black, Fine Motion, etc. (you can add your own card)
- Automatically trains Uma with stat prioritization
- Checks mood and handles debuffs automatically
- Rest and recreation management
- Skill point check for manual skill purchasing
- Stat caps to prevent overtraining specific stats
- Improved training logic with better support card handling
- Minimum support card requirements for training (Read Logic)
- Using Mumu emulator to not occupy the mouse.

### Getting Started

#### Requirements

- [Python 3.10+](https://www.python.org/downloads/)

#### Setup

##### Clone repository

```
git clone https://github.com/samsulpanjul/umamusume-auto-train.git
```

#### How to use

- Clone the code from git: https://www.youtube.com/watch?v=ZFFtMyOFPe8
- Install the latest Python version: https://www.python.org/downloads/ and add it to the PATH in your PC environment variable (https://www.youtube.com/watch?v=Ac3w0PjspWw&ab_channel=CyprienRusu)
- Open Windows PowerShell or Command Terminal
- Go to the folder of the code using cd /d (image) <img width="866" height="249" alt="image" src="https://github.com/user-attachments/assets/2f793ba7-90b0-4353-ad12-cc00a2f924d8" />
- Run "pip install -r requirements.txt"
- Open game, fullscreen, resolution MUST BE 1920 x 1080 (Change in Mumu Emulator setting)
- Run python main.py <img width="968" height="927" alt="image" src="https://github.com/user-attachments/assets/cce19ce0-6323-43a2-8757-c9e11849bd0d" />
- Read the REQUIREMENTS below

#### BEFORE YOU START

Make sure these conditions are met:

For Phone
- For phone, must use Mumu Emulator (https://www.mumuplayer.com/) and set screen resolution to 1280 x 720
- Your Uma must have already won the trophy for each race (the bot will skip the race)
- Turn off all confirmation pop-ups in game settings
- The game must be in the career lobby screen (the one with the Tazuna hint icon)
- Go to settings game to edit the race mode to "Path To Fame" to let race auto choose G1

For PC (PC IS NOT SUPPORTED FOR SECOND SCENARIO AND MORE)
- Screen resolution must be 1920x1080 for PC
- The game should be in full screen
- Your Uma must have already won the trophy for each race (the bot will skips the race)
- Turn off all confirmation pop-ups in game settings
- The game must be in the career lobby screen (the one with the Tazuna hint icon)
- Go to settings game to edit the race mode to Path To Fame to let race auto choose G1

#### Configuration

You can edit your configuration in `config.json`

```json
{
  "priority_stat": [
    "spd",
    "sta",
    "pwr"
  ],
  "minimum_mood": "GOOD",
  "maximum_failure": 15,
  "skill_point_cap": 200,
  "enable_skill_point_check": true,
  "min_support": 2,
  "stat_caps": {
    "spd": 1100,
    "sta": 1100,
    "pwr": 600,
    "guts": 300,
    "wit": 600
  },
  "saveDebugImages": false,
}
```

You can add more events according to your support cards in `events.json`
```json
{
  "Together for Tea": { # just a name for that event, anything works
    "key": "together for tea", # keyword to match the event, recommend only 2-3 first words
    "choice": 2, # choice to choose, start from 1
  }
}
```


##### Configuration Options

`priority_stat` (array of strings)
- Determines the training stat priority. The bot will focus on these stats in the given order of importance.
- Accepted values: `"spd"`, `"sta"`, `"pwr"`, `"guts"`, `"wit"`

`minimum_mood` (string)
- The lowest acceptable mood the bot will tolerate when deciding to train.
- Accepted values (case-sensitive): `"GREAT"`, `"GOOD"`, `"NORMAL"`, `"BAD"`, `"AWFUL"`
- **Example**: If set to `"NORMAL"`, the bot will train as long as the mood is `"NORMAL"` or better. If the mood drops below that, it'll go for recreation instead.

`maximum_failure` (integer)
- Sets the maximum acceptable failure chance (in percent) before skipping a training option.
- Example: 10 means the bot will avoid training with more than 10% failure risk.

`skill_point_cap` (integer) - 
- Maximum skill points before the bot prompts you to spend them.
- The bot will pause on race days and show a prompt if skill points exceed this cap.

`enable_skill_point_check` (boolean) - 
- Enables/disables the skill point cap checking feature.

`min_support` (integer) - 
- Minimum number of support cards required for training (default: 3).
- If no training meet the requirement, the bot will do race instead.
- WIT training requires at least 2 support cards regardless of this setting.
- If you want to turn this off, set it to 0

`stat_caps` (object) - 
- Maximum values for each stat. The bot will skip training stats that have reached their cap.
- Prevents overtraining and allows focusing on other stats.

`saveDebugImages` (boolean) - 
- Ignore unless you want to test the code

Make sure the values match exactly as expected, typos might cause errors.

#### Start

```
python main.py
```

To stop the bot, just press `Ctrl + C` in your terminal, or move your mouse to the top-left corner of the screen.

#### Training Logic

The bot uses an improved training logic system:

1. **Junior Year**: Prioritizes training in areas with the most support cards to quickly unlock rainbow training.
2. **Senior/Classic Year**: Prioritizes rainbow training (training with support cards of the same type). If no rainbow then use training with most support cards, or spirit/spirit-bomb or Aoharu
3. **Stat Caps**: Automatically skips training stats that have reached their configured caps.
4. **Support Requirements**: Ensures minimum support card requirements are met before training. If not enough support cards, do race instead.
5. **Rest Logic**: If energy is too low (every training have high failure rate) => Rest

#### Known Issues

- Some Uma that has special event/target goals (like Restricted Train Goldship or 2 G1 Race Oguri Cap) may not working. So please avoid using Goldship for training right now to keep your 12 million yen safe. For Oguri Cap, you can turn on Prioritize G1 race
- OCR might misread failure chance (e.g., reads 33% as 3%) and proceeds with training anyway.
- Sometimes it misdetects debuffs and clicks the infirmary unnecessarily (not a big deal).
- If you bring a friend support card (like Tazuna/Aoi Kiryuin) and do recreation, the bot can't decide whether to date with the friend support card or the Uma.
- The bot will skip "3 consecutive races warning" prompt for now

#### Contribute

If you run into any issues or something doesn't work as expected, please send an email to kazatashi1@gmail.com. Thank you!

## Tiếng Việt

### Giới thiệu
Bạn mệt mỏi vì dính phải những lần train xui vcl, bạn mệt mỏi khi phải cày bố mẹ cho Uma thì app này dành cho bạn. Đây là một app train Uma tự động.

Dự án này được lấy cảm hứng từ [shiokaze/UmamusumeAutoTrainer](https://github.com/shiokaze/UmamusumeAutoTrainer)

[Video demo](https://youtu.be/CXSYVD-iMJk)

### Tính năng
- Tự động chọn tùy chọn dựa trên năng lượng (năm 2, năm 3, năm mới, huấn luyện thêm). Một số sự kiện của Kitasan Black, Fine Motion, v.v. đã được code thẳng trong phần mềm (bạn có thể tự thêm event của thẻ của mình)
- Tự động huấn luyện Uma với chỉ số ưu tiên
- Kiểm tra Mood và xử lý debuff tự động
- Quản lý nghỉ ngơi và giải trí
- Kiểm tra điểm kỹ năng
- Giới hạn chỉ số để tránh huấn luyện quá mức
- Cải thiện logic huấn luyện với xử lý thẻ hỗ trợ tốt hơn
- Yêu cầu tối thiểu số thẻ hỗ trợ cho huấn luyện

### Bắt đầu

#### Yêu cầu
- [Python 3.10+](https://www.python.org/downloads/)

#### Cài đặt

##### Tải mã nguồn
```
git clone https://github.com/samsulpanjul/umamusume-auto-train.git
```

##### Hướng dẫn sử dụng
- Tải mã nguồn từ git: https://www.youtube.com/watch?v=ZFFtMyOFPe8
- Cài đặt Python mới nhất: https://www.python.org/downloads/, thêm Python vào PATH của máy (https://www.youtube.com/watch?v=Ac3w0PjspWw&ab_channel=CyprienRusu)
- Mở PowerShell hoặc Command Terminal
- Di chuyển đến thư mục mã nguồn bằng lệnh `cd /d` (xem hình minh họa)
- Chạy lệnh: `pip install -r requirements.txt`
- Mở game, để chế độ toàn màn hình, độ phân giải 1920 x 1080
- Chạy: `python main.py`
- Đọc phần YÊU CẦU bên dưới

### TRƯỚC KHI BẮT ĐẦU

Đảm bảo các điều kiện sau:

#### Giả lập điện thoại
- Dùng giả lập Mumu (https://www.mumuplayer.com/) và đặt độ phân giải 1280 x 720
- Uma đã thắng tất cả các cúp (bot sẽ bỏ qua các cuộc đua đã có cúp)
- Tắt tất cả các pop-up xác nhận trong cài đặt game
- Game phải ở màn hình career lobby (có biểu tượng Tazuna hint)
- Đặt usePhone thành true
- Vào setting game chỉnh race mode thành Path To Fame để race auto chọn G1 khi đua

#### Đối với PC (KO KHUYẾN KHÍCH DÙNG VÌ SẼ KO UPDATE KỂ TỪ SCENARIO 2)
- Độ phân giải màn hình phải là 1920x1080
- Game ở chế độ toàn màn hình
- Uma đã thắng tất cả các cúp (bot sẽ bỏ qua các cuộc đua đã có cúp)
- Tắt tất cả các pop-up xác nhận trong cài đặt game
- Game phải ở màn hình career lobby (có biểu tượng Tazuna hint)
- Vào setting game chỉnh race mode thành Path To Fame để race auto chọn G1 khi đua

### Cấu hình
Bạn có thể chỉnh sửa cấu hình trong `config.json`

```json
{
  "priority_stat": [
    "spd",
    "sta",
    "pwr"
  ],
  "minimum_mood": "GOOD",
  "maximum_failure": 15,
  "skill_point_cap": 200,
  "enable_skill_point_check": true,
  "min_support": 2,
  "stat_caps": {
    "spd": 1100,
    "sta": 1100,
    "pwr": 600,
    "guts": 300,
    "wit": 600
  },
  "saveDebugImages": false
}
```

Bạn cũng có thể thêm events và option vào trong file `events.json` dựa vào các thẻ support mà bạn có.
```json
{
  "Together for Tea": { # tên của event có thể đặt tùy ý
    "key": "together for tea", # từ khóa của event đó, viết liền và nên chọn 2-3 từ đầu tiên
    "choice": 2, # option để chọn, bắt đầu từ 1
  }
}
```

#### Tùy chọn cấu hình

- `priority_stat` (chữ): Xác định thứ tự ưu tiên huấn luyện chỉ số. Bot sẽ tập trung vào các chỉ số này theo thứ tự quan trọng.
  - Giá trị hợp lệ: `"spd"`, `"sta"`, `"pwr"`, `"guts"`, `"wit"`
- `minimum_mood` (chữ): Tâm trạng thấp nhất mà bot chấp nhận khi quyết định huấn luyện.
  - Giá trị hợp lệ (phân biệt hoa thường): `"GREAT"`, `"GOOD"`, `"NORMAL"`, `"BAD"`, `"AWFUL"`
  - **Ví dụ**: Nếu đặt là `"NORMAL"`, bot sẽ huấn luyện khi tâm trạng là `"NORMAL"` hoặc tốt hơn. Nếu thấp hơn, bot sẽ chọn giải trí.
- `maximum_failure` (số nguyên): Xác suất thất bại tối đa (phần trăm) trước khi chọn rest.
  - Ví dụ: 10 nghĩa là bot sẽ tránh các bài tập có rủi ro thất bại trên 10%.
- `skill_point_cap` (số nguyên): Điểm kỹ năng tối đa trước khi bot nhắc bạn sử dụng.
  - Bot sẽ tạm dừng vào ngày đua và hiển thị nhắc nhở nếu điểm kỹ năng vượt quá giới hạn này.
- `enable_skill_point_check` (yes/no): Bật/tắt tính năng kiểm tra giới hạn điểm kỹ năng.
- `min_support` (số nguyên): Số thẻ hỗ trợ tối thiểu cần thiết cho huấn luyện (mặc định: 3). Nếu không đủ, bot sẽ đua thay vì huấn luyện. Huấn luyện WIT chỉ cần tối thiểu 2 thẻ hỗ trợ. Nếu muốn tắt, đặt giá trị này là 0.
- `stat_caps` (object): Giá trị tối đa cho từng chỉ số. Bot sẽ bỏ qua huấn luyện các chỉ số đã đạt giới hạn.
- `saveDebugImages` (yes/no): Bỏ qua trừ khi bạn muốn kiểm tra mã nguồn.

Hãy đảm bảo các giá trị nhập đúng như yêu cầu, sai chính tả có thể gây lỗi.

### Khởi động

```
python main.py
```

Để dừng bot, nhấn `Ctrl + C` trong terminal, hoặc di chuyển chuột lên góc trên bên trái màn hình.

### Logic huấn luyện

Bot sử dụng hệ thống logic huấn luyện cải tiến:

1. **Junior Year**: Ưu tiên huấn luyện ở khu vực có nhiều thẻ hỗ trợ nhất để nhanh chóng mở khóa huấn luyện cầu vồng.
2. **Senior/Classic Year**: Ưu tiên chọn cầu vồng (có nhiều thẻ hỗ trợ cùng loại). Nếu ko có cầu vồng, sẽ dùng train nào có nhiều support card hay là spirit-bomb/spirit (Aoharu scenario)
3. **Giới hạn chỉ số**: Tự động bỏ qua huấn luyện các chỉ số đã đạt giới hạn.
4. **Yêu cầu thẻ hỗ trợ**: Đảm bảo đủ số thẻ hỗ trợ tối thiểu trước khi huấn luyện. Nếu không đủ, bot sẽ đua thay vì huấn luyện.
6. **Logic nghỉ ngơi**: Nếu năng lượng thấp (tất cả các bài tập đều có tỷ lệ thất bại cao) => Nghỉ ngơi

### Vấn đề đã biết
- Một số Uma có mục tiêu/sự kiện đặc biệt (như Goldship hoặc Oguri Cap) có thể không hoạt động đúng. Vui lòng tránh dùng Goldship để đảm bảo an toàn.
- OCR có thể đọc sai tỷ lệ thất bại (ví dụ: đọc 33% thành 3%) và vẫn tiếp tục huấn luyện.
- Đôi khi nhận diện debuff sai và nhấn vào infirmary không cần thiết (không ảnh hưởng nhiều).
- Luôn chọn tùy chọn trên cùng trong các sự kiện chuỗi.
- Nếu mang thẻ hỗ trợ bạn (Tazuna/Aoi Kiryuin) và giải trí, bot không thể quyết định hẹn hò với ai.
- Bot sẽ bỏ qua cảnh báo "3 cuộc đua liên tiếp" hiện tại

### TODO

- Thêm tùy chọn chiến lược đua (hiện tại chỉ có thể thay đổi thủ công)
- Đua các cuộc đua chưa có cúp
- Tự động mua kỹ năng (đã có một phần với quản lý điểm kỹ năng)
- Tự động hóa sự kiện Claw Machine
- Cải thiện độ chính xác OCR cho nhận diện tỷ lệ thất bại
- Thêm giới hạn số cuộc đua liên tiếp
- Thêm tự động thử lại khi đua thất bại
- Thêm theo dõi/đặt mục tiêu fan cho Senior year (Valentine, Fan Fest, Holiday Season)
- Thêm tùy chọn đua vào mùa hè (tháng 7-8)
- Cải thiện xử lý tùy chọn sự kiện

### Đóng góp

Nếu các bạn gặp vấn đề hoặc có ý tưởng để cải tiến app, vui lòng nhắn tin tới email kazatashi1@gmail.com
