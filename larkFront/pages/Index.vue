<template>
  <el-container class="Index">
    <el-header>
      钉钉机器人定时消息
      <el-button type="primary" icon="el-icon-circle-plus" @click="handleAddMessage">添加</el-button>
    </el-header>
    <el-main class="main">
      <el-table :data="messageList" style="width: 100%">
        <el-table-column label="TOKEN">
          <template slot-scope="scope">
            <span>{{ scope.row.token }}</span>
          </template>
        </el-table-column>
        <el-table-column label="运行时间">
          <template slot-scope="scope">
            <span>{{describeTime(scope.row.time)}}</span>
          </template>
        </el-table-column>
        <el-table-column label="消息类型">
          <template slot-scope="scope">
            <span>{{scope.row.message.type}}</span>
          </template>
        </el-table-column>
        <el-table-column label="消息">
          <template slot-scope="scope">{{describeMessage(scope.row.message)}}</template>
        </el-table-column>
        <el-table-column label="操作">
          <template slot-scope="scope">
            <el-button size="mini" @click="handleEdit(scope.$index, scope.row)">编辑</el-button>
            <el-button size="mini" type="danger" @click="handleDelete(scope.$index, scope.row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-main>
    <el-footer height="30">This is Footer</el-footer>
    <el-dialog :title="dialog.title" :visible.sync="dialog.visible" width="90%" height="90%" center>
      <el-form :model="form" label-width="100px" size="mini">
        <el-form-item label="时间间隔">
          <el-input-number v-model="form.time.interval_count" :step="1"></el-input-number>
          <span v-if="form.time.interval_count==0" style="font-size:10px;color:red">*时间间隔为0表示只执行一次</span>
        </el-form-item>

        <el-form-item label="时间间隔单位">
          <el-select v-model="form.time.interval_unit" clearable placeholder="请选择">
            <el-option
              v-for="item in timeIntervalUnitOptions"
              :key="item.value"
              :label="item.label"
              :value="item.value"
              :disabled="form.time.interval_count==0"
            ></el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="具体时间">
          <el-time-picker
            v-model="form.time.clock"
            :picker-options="pickerOption"
            :disabled="form.time.interval_unit=='seconds'||form.time.interval_unit==null"
            placeholder="选择时间"
          ></el-time-picker>
        </el-form-item>
        <el-form-item label="回调链接">
          <el-input v-model="form.token" style="width:90%" placeholder="回调链接"></el-input>
        </el-form-item>
        <el-form-item label="消息类型">
          <el-radio-group v-model="form.message.type" size="small">
            <el-radio-button label="text" border>文本消息</el-radio-button>
            <el-radio-button label="markdown" border>Markdown</el-radio-button>
            <el-radio-button label="link" border>链接消息</el-radio-button>
            <el-radio-button label="feed" border>Feed流</el-radio-button>
            <el-radio-button label="action_card" border>ActionCard</el-radio-button>
            <el-radio-button label="single_action_card" border>SingleActionCard</el-radio-button>
          </el-radio-group>
        </el-form-item>
        <div v-if="form.message.type=='text'">
          <el-form-item label="消息内容">
            <el-input
              type="textarea"
              :rows="10"
              placeholder="请输入内容"
              v-model="form.message.message.text"
            ></el-input>
          </el-form-item>
          <el-form-item label="at所有人">
            <el-switch
              v-model="form.message.message.at_all"
              active-color="#13ce66"
              inactive-color="#ff4949"
            ></el-switch>
          </el-form-item>
        </div>
        <div v-else-if="form.message.type=='markdown'">
          <el-form-item label="标题">
            <el-input type="message" placeholder="标题" v-model="form.message.message.title"></el-input>
          </el-form-item>
          <el-form-item label="内容">
            <el-input
              type="textarea"
              :rows="10"
              placeholder="请输入内容"
              v-model="form.message.message.text"
            ></el-input>
          </el-form-item>
        </div>
        <div v-else-if="form.message.type=='link'">
          <el-form-item label="标题">
            <el-input type="message" placeholder="标题" v-model="form.message.message.title"></el-input>
          </el-form-item>
          <el-form-item label="内容">
            <el-input
              type="textarea"
              :rows="10"
              placeholder="请输入内容"
              v-model="form.message.message.text"
            ></el-input>
          </el-form-item>
          <el-form-item label="链接">
            <el-input type="message" placeholder="内容" v-model="form.message.message.message_url"></el-input>
          </el-form-item>
          <el-form-item label="图片">
            <el-input type="message" placeholder="内容" v-model="form.message.message.pic_url"></el-input>
          </el-form-item>
        </div>
        <div v-else-if="form.message.type=='feed'">
          <div v-for="(row,ind) in form.message.message.rows" :key="ind">
            <el-form-item label="标题">
              <el-input type="message" placeholder="标题" v-model="row.title"></el-input>
            </el-form-item>
            <el-form-item label="文本链接">
              <el-input type="message" placeholder="文本链接" v-model="row.messageURL"></el-input>
            </el-form-item>
            <el-form-item label="图片链接">
              <el-input type="message" placeholder="图片链接" v-model="row.picURL"></el-input>
            </el-form-item>
          </div>
          <el-button @click="addRowToFeed()">添加</el-button>
          <el-button @click="removeRowFromFeed()">删除</el-button>
        </div>
        <div v-else-if="form.message.type=='single_action_card'">
          <el-form-item label="标题">
            <el-input type="message" placeholder="消息通知标题" v-model="form.message.message.title"></el-input>
          </el-form-item>
          <el-form-item label="Markdown文本">
            <el-input
              type="textarea"
              :rows="10"
              placeholder="文本"
              v-model="form.message.message.text"
            ></el-input>
          </el-form-item>
          <el-form-item label="single标题">
            <el-input
              type="message"
              placeholder="single标题"
              v-model="form.message.message.single_title"
            ></el-input>
          </el-form-item>
          <el-form-item label="singleURL">
            <el-input
              type="message"
              placeholder="singleURL"
              v-model="form.message.message.single_url"
            ></el-input>
          </el-form-item>
          <el-form-item label="按钮方向">
            <el-radio v-model="form.message.message.button_orientation" label="0">横向</el-radio>
            <el-radio v-model="form.message.message.button_orientation" label="1">纵向</el-radio>
          </el-form-item>
          <el-form-item label="头像">
            <el-radio v-model="form.message.message.hide_avatar" label="0">显示头像</el-radio>
            <el-radio v-model="form.message.message.hide_avatar" label="1">隐藏</el-radio>
          </el-form-item>
        </div>
        <div v-else-if="form.message.type=='action_card'">
          <el-form-item label="标题">
            <el-input type="message" placeholder="标题" v-model="form.message.message.title"></el-input>
          </el-form-item>
          <el-form-item label="Markdown文本">
            <el-input
              type="textarea"
              :rows="10"
              placeholder="Markdown文本"
              v-model="form.message.message.text"
            ></el-input>
          </el-form-item>
          <div v-for="(btn,ind) in form.message.message.buttons" :key="ind">
            <el-form-item label="按钮文本">
              <el-input v-model="btn.title" placeholder="按钮文本"></el-input>
            </el-form-item>
            <el-form-item label="按钮链接">
              <el-input v-model="btn.actionURL" placeholder="按钮链接"></el-input>
            </el-form-item>
          </div>
          <el-button @click="addActionButton">添加按钮</el-button>
          <el-button @click="removeActionButton">删除按钮</el-button>
          <el-form-item label="按钮方向">
            <el-radio v-model="form.message.message.button_orientation" label="0">横向</el-radio>
            <el-radio v-model="form.message.message.button_orientation" label="1">纵向</el-radio>
          </el-form-item>
          <el-form-item label="头像">
            <el-radio v-model="form.message.message.hide_avatar" label="0">显示头像</el-radio>
            <el-radio v-model="form.message.message.hide_avatar" label="1">隐藏</el-radio>
          </el-form-item>
        </div>

        <div v-else>不支持的消息类型</div>
      </el-form>
      <span slot="footer" class="dialog-footer">
        <el-button @click="dialog.visible = false">取 消</el-button>
        <el-button type="primary" @click="submitForm">确 定</el-button>
      </span>
    </el-dialog>
  </el-container>
</template>
<script>
const axios = require("axios");
var messageTypeFields = {
  text: ["text", "at_all"],
  markdown: ["title", "text"],
  link: ["title", "text", "pic_url", "message_url"],
  action_card: ["buttons", "button_orientation", "title", "text"],
  single_action_card: ["single_title", "title", "text", "single_url"],
  feed: ["rows"]
};
var textUrl = "https://cnblogs.com/weiyinfu";
var imageUrl = "https://image.ijq.tv/201806/06/10-12-53-11-26.jpg";
export default {
  data() {
    //创建form时的默认值
    return {
      messageList: [],
      timeIntervalUnitOptions: [],
      form: this.getDefaultForm(),
      dialog: {
        title: "创建定时消息",
        visible: false
      }
    };
  },
  computed: {
    pickerOption() {
      const intervalUnit = this.form.time.interval_unit;
      if (intervalUnit == "seconds") {
        return null;
      }
      var selectableRange = "00:00:00-23:59:59";
      if (intervalUnit == "minutes") {
        selectableRange = "00:00:00-00:01:00";
      } else if (intervalUnit == "hours") {
        selectableRange = "00:00:00-00:59:59";
      }
      return {
        selectableRange
      };
    }
  },

  mounted() {
    axios.get("/api/get_interval_list").then(resp => {
      this.timeIntervalUnitOptions = resp.data.map(timeUnit => {
        return {
          label: timeUnit,
          value: timeUnit
        };
      });
      this.form.time.interval_unit = this.timeIntervalUnitOptions[0].value;
    });
    this.updateMessageList();
  },
  methods: {
    addRowToFeed() {
      this.form.message.message.rows.push({
        title: "title",
        messageURL: textUrl,
        picURL: imageUrl
      });
    },
    removeRowFromFeed() {
      this.form.message.message.rows.pop();
    },
    addActionButton() {
      this.form.message.message.buttons.push({
        title: "push",
        actionURL: textUrl
      });
    },
    removeActionButton() {
      this.form.message.message.buttons.pop();
    },
    updateMessageList() {
      axios.get("/api/select_message").then(resp => {
        this.messageList = resp.data;
      });
    },
    handleEdit(ind, row) {
      this.dialog.visible = true;
      this.form = row;
      this.form.messageId = row.id;
    },
    handleDelete(ind, row) {
      axios
        .get("/api/delete_message", {
          params: {
            message_id: row.id
          }
        })
        .then(resp => {
          if (resp.data == "ok") {
            this.$message("删除数据成功");
            this.updateMessageList();
          } else {
            this.$message("删除数据失败");
          }
        });
    },
    handleAddMessage() {
      this.form.messageId = null;
      this.form = this.getDefaultForm();
      this.dialog.visible = true;
    },
    getDefaultForm() {
      return {
        messageId: null, //仅在编辑消息时有效
        time: {
          interval_count: 0,
          interval_unit: null,
          clock: null
        },
        message: {
          //message必须是一个非常大的超集
          type: "text",
          message: {
            text: "",
            at_all: false,
            buttons: [],
            button_orientation: "0",
            title: null,
            rows: [],
            single_title: null,
            single_url: textUrl,
            pic_url: imageUrl,
            message_url: textUrl,
            hide_avatar: "0"
          }
        },
        token:
          "https://oapi.dingtalk.com/robot/send?access_token=b13658ff4b9c71a8712a7db093f7efd37bd05c837efe7f80f183b1b068d7c61e"
      };
    },
    submitForm() {
      var form = JSON.parse(JSON.stringify(this.form));
      var message = {};
      var messageType = form.message.type;
      for (var k in form.message.message) {
        if (messageTypeFields[messageType].indexOf(k) != -1) {
          message[k] = form.message.message[k];
        }
      }
      console.log("sending" + messageType);
      console.log(message);
      form.message.message = message;
      if (this.form.messageId) {
        //编辑消息
        this.dialog.visible = false;

        axios
          .get("/api/update_message", {
            params: { data: JSON.stringify(form) }
          })
          .then(resp => {
            console.log(resp.data);
            this.dialog.visible = false;
            this.updateMessageList();
            this.$message("修改消息成功");
          })
          .catch(e => {})
          .finally(() => {});
      } else {
        //创建消息
        axios
          .get("/api/insert_message", {
            params: { data: JSON.stringify(form) }
          })
          .then(resp => {
            console.log(resp.data);
            if (resp.data == "ok") {
              this.dialog.visible = false;
              this.$message("添加消息成功");
              this.updateMessageList();
            } else {
              this.$message("添加消息失败");
            }
          })
          .catch(e => {})
          .finally(() => {});
      }
    },
    describeTime(time) {
      if (time.intervalCount == 0) {
        return `只运行一次：${time.intervalUnit} ${time.clock}`;
      } else {
        return `${time.interval_count} ${time.interval_unit} ${time.clock ||
          ""}`;
      }
    },
    describeMessage(message) {
      if (message.type == "text") {
        return message.text;
      } else {
        console.log(message);
        return "不支持的类型";
      }
    }
  }
};
</script>
<style lang="less">
@import url("../common.less");

.Index {
  .fillParent();
  .myFrame();
  .el-header {
    font-family: "微软雅黑";
    font-size: 24px;
    display: flex;
    align-items: center;
    justify-content: space-between;
  }
}
</style>
